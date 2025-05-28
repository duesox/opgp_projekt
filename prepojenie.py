import os
import sys
import threading
import uuid
import netifaces
import select
import comtypes.client as cc
from comtypes import COMError
import ctypes

import json
import socket
import time

PORT = 4037
MPORT = 4038  # multicast port
MGROUP = '224.0.0.123'
UUID_FILE = 'uuid.txt'
PROTOCOLS = {6: 'tcp', 17: 'udp'}


# ip add return as bits
def ip2bytes(addr):
    return socket.inet_aton(addr)


def send_message(message, sock):
    sock.send(json.dumps(message).encode())


# nova firewall rule - vstup prot ID, port, dir: in - 1, out - 2
def _create_firewall_rule(protocol, port, direction):
    print(protocol, port, direction)
    fw_policy = cc.CreateObject("HNetCfg.FwPolicy2")
    rules = fw_policy.Rules
    rule = cc.CreateObject("HNetCfg.FWRule")
    if direction == 1:
        dire = "In"
    else:
        dire = "Out"
    rule.Name = f"4Connect {PROTOCOLS[protocol]} {dire}"
    rule.Direction = direction
    rule.Protocol = protocol
    rule.LocalPorts = str(port)
    rule.Action = 1
    rule.Enabled = 1
    rules.Add(rule)
    return rule.Name


# kontrola, ci uz nejake firewall rules co chceme skontrolovat existuju, ak ano, vracia sa zoznam existujucich rules
def _check_firewall_rules(rules_to_check):
    existing_rules = []
    try:
        fw_policy = cc.CreateObject("HNetCfg.FwPolicy2")
        rules = fw_policy.Rules
        for rule in rules:
            if not rule.Enabled or rule.Action != 1:
                continue
            for target in rules_to_check:
                if (rule.Protocol == target['protocol'] and
                        rule.Direction == target['direction'] and
                        str(target['port']) in rule.LocalPorts.split(',')):
                    existing_rules.append({'protocol': target['protocol'],
                                           'port': target['port'],
                                           'direction': target['direction']})
    except COMError as e:
        print("Check - chyba pri pristupe ku Firewall -", {e})
    return existing_rules


# sprava celeho procesu vytvarania rules
def _manage_firewall_rules():
    required_rules = [
        {'protocol': 6, 'port': 4037, 'direction': 1},
        {'protocol': 6, 'port': 4037, 'direction': 2},
        {'protocol': 17, 'port': 4038, 'direction': 1},
        {'protocol': 17, 'port': 4038, 'direction': 2}
    ]
    try:
        existing = _check_firewall_rules(required_rules)
        for rule in existing:
            if rule in required_rules:
                del required_rules[required_rules.index(rule)]
        print(existing)
        print(len(required_rules))
        print(required_rules)
        if len(required_rules) > 0:
            if not is_admin():
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
                sys.exit()

        created = []
        for e in existing:
            print({e['protocol'], e['port'], e['direction']})
        for rule in required_rules:
            rule_name = _create_firewall_rule(rule['protocol'], rule['port'], rule['direction'])
            created.append(rule_name)
        if len(created) > 0:
            for name in created:
                print(f"nova firewall rule: {name}")
            time.sleep(5)
            ctypes.windll.shell32.ShellExecuteW(None, "open", sys.executable, f'"{sys.argv[0]}" --no-elevate', None, 1)
            sys.exit()
        else:
            print("uz vsetky rules existuju")
    except COMError as e:
        print("Chyba pri pristupe ku Firewall -", {e})
    except Exception as e:
        print("chyba", e)


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        print(e)
        return False


class Networking:
    def __init__(self):
        self._game_sock = None
        self._devices = {}
        self._devices_lock = threading.Lock()
        self._self_address = socket.gethostbyname(socket.gethostname())
        self._discovering = False
        self._nic = 0

        self._nick = None

        """
        self._send_thread = None
        self._recv_thread = None
        self._del_old_dev_thread = None
        """
        self._tcp_recv_thread = None
        self._disc_thread = None
        self._stop_event = threading.Event()

        self._game_started = False
        # callbacky
        self.on_move_recieved = lambda x: None
        self.on_settings_changed = lambda x_size, y_size, max_wins: None

        self.on_game_invite = lambda nick, uuid: None
        self.on_game_invite_rejected = lambda: None

        self.on_connect = lambda: None
        self.on_disconnect = lambda: None
        self.on_new_discovery = lambda devices: None

        self.no_devices_found = lambda cas: None

        self.on_request_restart = lambda: None
        self.on_game_restart = lambda: None

        self.on_request_retry = lambda: None
        self.on_game_retry = lambda: None

        self._x_size = 7
        self._y_size = 6
        self._max_wins = 3

        self._tcp_recieving = False

        if os.path.exists(UUID_FILE):
            with open(UUID_FILE, 'r') as f:
                riadky = f.readline().strip().split()
                self._uuid = str(riadky[0])
                if len(riadky) == 2:
                    self.nick = str(riadky[1])

        else:
            self._uuid = str(uuid.uuid4())
            with open(UUID_FILE, 'w') as f:
                f.write(str(self._uuid))

        _manage_firewall_rules()

    def get_uuid(self):
        print(self._uuid)

    def set_nickname(self, nickname):
        self._nick = nickname

    def get_nickname(self):
        return self._nick

    def get_devices(self):
        with self._devices_lock:
            return self._devices.copy()

    def set_game_settings(self, x_size, y_size, max_wins):
        self._x_size = x_size
        self._y_size = y_size
        self._max_wins = max_wins

    def get_game_settings(self):
        return self._x_size, self._y_size, self._max_wins

    def start_discovery(self):
        self._nic = 0
        self._discovering = True
        self._disc_thread = threading.Thread(target=self.discovery_loop)
        self._disc_thread.start()
        print('zacate vyhladavanie')

    # toto treba osetrit, aby pri vypnuti programu sa vykonalo spolocne so stop_tcp_listen
    #
    #
    def stop_discovery(self):
        self._discovering = False
        self._stop_event.set()
        if self._disc_thread is not None:
            while self._disc_thread.is_alive():
                self._disc_thread.join(timeout=1)
        print("ukoncene sietovanie")

    def discovery_loop(self):
        with not self._stop_event.is_set():
            previous_send_recv = 0
            previous_del = 0
            recvs = {}
            send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            send.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            send.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)
            for i in netifaces.interfaces():
                if "Virtual" in i or "virtual" in i or "loop" in i or "Loop" in i or 2 not in netifaces.ifaddresses(
                        i).keys():
                    if i not in ['vpn', 'Vpn', 'VPN']:
                        continue
                print(i)
                j = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                j.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                j.bind(('', MPORT))
                print(netifaces.ifaddresses(i)[2][0]['addr'])
                mreq = ip2bytes(MGROUP) + ip2bytes(netifaces.ifaddresses(i)[2][0][
                                                       'addr'])  # tu musi byt presne zadana ipcka interfacu s inteom - bud ethernet alebo skor wifi
                j.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
                j.settimeout(1)
                j.setblocking(False)
                recvs[j] = netifaces.ifaddresses(i)[2][0]['addr']

            previous_device = time.time()

            while self._discovering:
                current_time = time.time()
                if current_time - previous_send_recv > 5:
                    # posielanie hello do multicast group
                    previous_send_recv = current_time
                    sprava = json.dumps(
                        {
                            'app': 'connect43sa',
                            'nick': self._nick,
                            "type": "discovery",
                            "timestamp": int(time.time()),
                            "uuid": self._uuid,
                        }
                    ).encode()
                    print('send -', sprava)
                    send.sendto(sprava, (MGROUP, MPORT))
                    # print(f"sprava poslana: {sprava}")
                    # prijimanie sprav z roznych socketov, ak tam nejake su
                    ready_socks = select.select(list(recvs.keys()), [], [], 1)[0]
                    if not ready_socks:
                        self._nic += 1

                    else:
                        self._nic = 0
                        try:
                            for recv in ready_socks:
                                data, addr = recv.recvfrom(1024)
                                message = json.loads(data.decode())
                                if message["app"] == "connect43sa" and message["type"] == "discovery" and message[
                                    'uuid'] != self._uuid:
                                    """
                                    for r in list(recvs.keys()):
                                        if r != recv:
                                            print('DEL', recvs[r])
                                            del recvs[r]
                                    """
                                    ip = addr[0]
                                    with self._devices_lock:
                                        if ip in self._devices:
                                            if self._devices[ip]['last_ping'] == message['timestamp']:
                                                print("skipnuty rovnaky timestamp")
                                                continue
                                            self._devices[ip]['last_ping'] = int(time.time())
                                            print("zmeneny timestamp")
                                        else:
                                            self._devices[ip] = {
                                                'nick': message['nick'],
                                                'uuid': message['uuid'],
                                                'last_ping': int(time.time()),
                                            }
                                            # TODO toto potom treba presunut za except
                                            self.on_new_discovery(self._devices)
                                            print("pridane zar")
                                    print(f"sprava prijata: {message}")
                                    previous_device = current_time
                        except (socket.timeout, json.JSONDecodeError):
                            continue

                if self._nic >= 6:
                    # mozno toto vyuzijeme, ked po dlhsom discovery sa nikto neobjavi
                    self.no_devices_found(current_time - previous_device)
                if current_time - previous_del > 15:
                    previous_del = current_time
                    with self._devices_lock:
                        old_ips = [ip for ip, info in self._devices.items() if current_time - info['last_ping'] > 15]
                        for ip in old_ips:
                            del self._devices[ip]
                            print(f'vymazana stara ip: {ip}')
                    print(self._devices)
                    self.on_new_discovery(self._devices)
                    if len(self._devices) == 0:
                        previous_device = current_time
                time.sleep(5)
            send.close()

    def tcp_listener_loop(self):
        while self._tcp_recieving:
            data = self._game_sock.recv(1024)
            if data:
                self.handle_message(data)

    # zapne sa pri prichode a vypne sa pri odchode z discovery/hry
    def start_tcp_listen(self):
        self._tcp_recieving = True
        self._tcp_recv_thread = threading.Thread(target=self.tcp_listener_loop).start()

    def stop_tcp_listen(self):
        self._tcp_recieving = False
        if self._tcp_recv_thread is not None:
            self._tcp_recv_thread.join()

    def connect_to_client(self, uuid_game, alr):
        with self._devices_lock:
            for ip, info in self._devices.items():
                if info['uuid'] == uuid_game:
                    address = ip
                    break
        try:
            self._game_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._game_sock.connect((address, PORT))
            if alr == 0:
                self.game_accept(address, accept=1)
            self._game_started = True
            self.on_connect()
        except (socket.error, ConnectionRefusedError) as e:
            self._game_sock = None
            print(f"Nastala chyba pri pripajani: {e}")

    def handle_message(self, recv):
        message = json.loads(recv.decode())
        if 'uuid' not in message.keys() or message['uuid'] == self._uuid:
            pass
        else:
            action = message['type']
            if action == 'accept' and self._game_started is False:
                self.handle_accept(message)
            elif action == 'disconnect':
                self.handle_disconnect()
            elif action == 'move':
                self.handle_move(message)
            elif action == 'settings':
                self.handle_settings(message)
            elif action == 'restart':
                self.handle_restart(message)
            elif action == 'retry':
                self.handle_retry(message)
            else:
                print("Invalid message type")

    def handle_accept(self, message):
        if message['confirm'] == 'confirm':
            self.on_game_invite(message['nick'], message['uuid'])  # tu si pouzivatel aj nastavi nastavenia hry, ze ako velka bude
        elif message['confirm'] == 'confirmed':
            self.connect_to_client(message['uuid'], 1)
        elif message['confirm'] == 'rejected':
            self.on_game_invite_rejected()

    def handle_disconnect(self):
        if self._game_sock is not None:
            self._game_sock.close()
            self._game_sock = None
            self._game_started = False
            self.on_disconnect()

    def handle_move(self, message):
        x = message['x']
        self.on_move_recieved(x)

    def handle_settings(self, message):
        x_size = message['x_size']
        y_size = message['y_size']
        max_wins = message['max_wins']
        self.on_settings_changed(x_size, y_size, max_wins)

    def handle_restart(self, message):
        if message['restart'] == 'ask':
            self.on_request_restart()
        elif message['restart'] == 'yes':
            self.on_game_restart()

    def handle_retry(self, message):
        if message['retry'] == 'ask':
            self.on_request_retry()
        elif message['retry'] == 'yes':
            self.on_game_retry()

    # Poslanie pozvanky na hru – preposlanie do 2. zariadenia, nepovinny 2. parameter - 0 poslat pozvanku, 1 potvrdzujem poznamku, 2 odmietnuta pozvanka
    def game_accept(self, target_address, x_size=7, y_size=6, max_wins=3, accept=0):
        if '.' not in target_address:
            for ip, info in self._devices.items():
                if info['uuid'] == target_address:
                    target_address = ip
                    break
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as accept_sock:
            accept_sock.connect((target_address, PORT))
            if accept == 0:
                confirm = 'confirm'
                self.set_game_settings(x_size, y_size, max_wins)
                message = {'app': 'connect43sa', 'type': 'accept', 'uuid': self._uuid, 'ip': self._self_address,
                           'confirm': confirm, 'x_size': x_size, 'y_size': y_size, 'max_wins': max_wins}
            elif accept == 1:
                confirm = 'confirmed'
                message = {'app': 'connect43sa', 'type': 'accept', 'uuid': self._uuid, 'ip': self._self_address,
                           'confirm': confirm}
            else:
                confirm = 'rejected'
                self.set_game_settings(x_size, y_size, max_wins)
                message = {'app': 'connect43sa', 'type': 'accept', 'uuid': self._uuid, 'ip': self._self_address,
                           'confirm': confirm}
            send_message(message, accept_sock)

    def send_move(self, x):
        message = {'app': 'connect43sa', 'type': 'move', 'uuid': self._uuid, 'x': x}
        send_message(message, self._game_sock)


if __name__ == "__main__":
    net = Networking()
    try:
        net.get_uuid()
        # print(net.handle_message(b'{"type": "disconnect"}'))
        net.start_discovery()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        net.stop_discovery()
        net.stop_tcp_listen()
        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)
