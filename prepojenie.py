import os
import threading
import uuid
import struct

import json
import socket
import time

PORT = 40337
MPORT = 40338 # multicast port
MGROUP = '224.1.1.3'
UUID_FILE = 'uuid.txt'

# ip add return as bits
def ip2bytes(addr):
    return socket.inet_aton(addr)


def send_message(message, sock):
    sock.send(json.dumps(message).encode())


class Networking:
    def __init__(self):
        self._game_sock = None
        self._devices = {}
        self._devices_lock = threading.Lock()
        self._self_address = socket.gethostbyname(socket.gethostname())
        self._discovering = False

        self._nick = None

        self._send_thread = None
        self._recv_thread = None
        self._del_old_dev_thread = None


        if os.path.exists(UUID_FILE):
            with open(UUID_FILE, 'r') as f:
                self._uuid = str(f.readline().strip())
        else:
            self._uuid = str(uuid.uuid4())
            with open(UUID_FILE, 'w') as f:
                f.write(str(self._uuid))

    def get_uuid(self):
        print(self._uuid)

    def set_nickname(self, nickname):
        self._nick = nickname

    def get_nickname(self):
        return self._nick

    def get_devices(self):
        return self._devices

    # odosielanie multicast sprav
    def send_discovery_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        while self._discovering:
            sprava = json.dumps(
                {
                    'nick': self._nick,
                    "type": "discovery",
                    "timestamp": int(time.time()),
                    "uuid": self._uuid,
                }
            ).encode()
            print('send -',sprava)
            sock.sendto(sprava, (MGROUP, MPORT))
            # print(f"sprava poslana: {sprava}")
            time.sleep(5)

    def recv_discovery_loop(self):
        print('recv discovery')
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        sock.bind(('', MPORT))
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, ip2bytes(self._self_address))
        mreq = ip2bytes(MGROUP) + ip2bytes(self._self_address)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        sock.settimeout(10)
        while self._discovering:
            try:
                data, addr = sock.recvfrom(1024)
                message = json.loads(data.decode())
                if message['type'] == 'discovery' and message['uuid'] != self._uuid:
                    print(message)
                    ip = addr[0]
                    with self._devices_lock:
                        self._devices[ip] = {
                            'nick': message['nick'],
                            'uuid': message['uuid'],
                            'last_ping': time.time(),
                        }
                    print(f"sprava prijata: {message}")
            except (socket.timeout, json.JSONDecodeError):
                continue

    # odstranenie starych ipciek zo zoznamu, ak zariadenie nedostalo ping za poslednych 15 sekund
    def del_old_devices(self):
        while self._discovering:
            current_time = time.time()
            with self._devices_lock:
                old_ips = [ip for ip, info in self._devices.items() if current_time - info['last_ping'] > 15]
                for ip in old_ips:
                    print('del old - '+ip)
                    del self._devices[ip]
                    print(f'vymazana stara ip: {ip}')
            print(self._devices)
            time.sleep(5)

    # zaciatok periodickeho vyhladavania a prijimania hracov na hru, s tym ze tieto procesy bezia samostatne
    def start_discovery(self):
        self._discovering = True
        self._send_thread = threading.Thread(target=self.send_discovery_loop)
        self._recv_thread = threading.Thread(target=self.recv_discovery_loop)
        self._del_old_dev_thread = threading.Thread(target=self.del_old_devices)
        self._send_thread.start()
        self._recv_thread.start()
        self._del_old_dev_thread.start()
        # print('zacate vyhladavanie')

    def stop_discovery(self):
        self._discovering = False
        if self._send_thread is not None:
            self._send_thread.join()
        if self._recv_thread is not None:
            self._recv_thread.join()
        if self._del_old_dev_thread is not None:
            self._del_old_dev_thread.join()
        # print("ukoncene vyhladavanie")



    def connect_to_client(self, address):
        try:
            self._game_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._game_sock.connect((address, PORT))
            self.game_accept(address, 1)
        except(socket.error, ConnectionRefusedError) as e:
            self._game_sock = None
            print(f"Nastala chyba pri pripajani: {e}")


    def handle_message(self, recv):
        message = json.loads(recv.decode())
        action = message['type']
        if action == 'accept':
            return self.handle_accept(message)
        elif action == 'disconnect':
            return self.handle_disconnect()
        elif action == 'move':
            return self.handle_move(message)
        elif action == 'settings':
            return self.handle_settings(message)
        else:
            print("Invalid type")

    def handle_accept(self, message):
        if message['confirm'] == 'confirm':
            return {'type': 'accept', 'confirm': 'choose'} # bude treba, aby este pouzivatel potvrdil alebo odmietol pozvanku
        elif message['confirm'] == 'confirmed':
            self.connect_to_client(message['address'])
            return {'type': 'accept', 'confirm': 'confirmed'}
        elif message['confirm'] == 'rejected':
            return {'type': 'accept', 'confirm': 'rejected'}

    def handle_disconnect(self):
        if self._game_sock is not None:
            self._game_sock.close()
            self._game_sock = None
        return {'type': 'disconnect'}

    def handle_move(self, message):
        x = message['x']
        return {'type': 'move', 'x': x}

    def handle_settings(self, message):
        x_size = message['x_size']
        y_size = message['y_size']
        max_wins = message['max_wins']

        return {'type': 'settings', 'x_size': x_size, 'y_size': y_size, 'max_wins': max_wins}

    # Prijatie pozvanky na hru – preposlanie do 2. zariadenia, nepovinny 2. parameter - 0 default prijat, 1 prijata pozvanka, 2 odmietnuta pozvanka
    def game_accept(self, target_address, accept=0):
        accept_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        accept_sock.connect((target_address, PORT))
        if accept == 0:
            confirm = 'confirm'
        elif accept == 1:
            confirm = 'confirmed'
        else:
            confirm = 'rejected'
        message = {'type': 'accept', 'uuid': self._uuid, 'ip': self._self_address, 'confirm': confirm}
        send_message(message, accept_sock)

    def send_move(self, x):
        message = {'type': 'move', 'uuid': self._uuid, 'x': x}
        send_message(message, self._game_sock)


if __name__ == "__main__":
    net = Networking()
    net.get_uuid()
    print(net.handle_message(b'{"type": "disconnect"}'))
    net.start_discovery()
