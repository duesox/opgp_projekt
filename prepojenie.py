import os
import sys
import netifaces
import select
import comtypes.client as cc
from comtypes import COMError
import ctypes

import json
import socket
import time

from ukladanie import Saving

PORT = 4037
MPORT = 4038  # multicast port
MGROUP = '224.0.0.123'
PROTOCOLS = {6: 'tcp', 17: 'udp'}


# ip add return as bits
def ip2bytes(addr):
    return socket.inet_aton(addr)


def send_message(message, sock):
    sock.send(json.dumps(message).encode())


# nova firewall rule - vstup prot ID, port, dir: in - 1, out - 2
def _create_firewall_rule(protocol, port, direction):
    #print(protocol, port, direction)
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
        # print(existing)
        # print(len(required_rules))
        # print(required_rules)
        if len(required_rules) > 0:
            if not is_admin():
                import pygame
                pygame.init()
                screen = pygame.display.set_mode((700, 400))
                pygame.display.set_caption("Dôležité upozornenie")
                font = pygame.font.SysFont("Arial", 24)
                small_font = pygame.font.SysFont("Arial", 20)

                lines = [
                    "Na správne fungovanie hry je potrebné udeliť administrátorské práva.",
                    "Tie slúžia na nastavenie výnimky vo firewalle pre sieťovú komunikáciu.",
                    "",
                    "Prosím potvrďte to v nasledujúcom dialógu (ak sa zobrazí),",
                    "inak nebude možné hrať multiplayer režim."
                ]

                ok_button = pygame.Rect(250, 300, 200, 50)

                showing = True
                while showing:
                    screen.fill((255, 255, 210))
                    for i, line in enumerate(lines):
                        text = font.render(line, True, (0, 0, 0))
                        screen.blit(text, (50, 40 + i * 40))

                    pygame.draw.rect(screen, (255, 0, 0), ok_button, border_radius=10)
                    pygame.draw.rect(screen, (255, 255, 0), ok_button.inflate(-10, -10), border_radius=10)
                    text = small_font.render("Rozumiem", True, (0, 0, 0))
                    text_rect = text.get_rect(center=ok_button.center)
                    screen.blit(text, text_rect)

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            exit()
                        elif event.type == pygame.MOUSEBUTTONDOWN and ok_button.collidepoint(event.pos):
                            showing = False

                    pygame.display.flip()
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
                sys.exit()

        created = []
        # for e in existing:
        # print({e['protocol'], e['port'], e['direction']})
        for rule in required_rules:
            rule_name = _create_firewall_rule(rule['protocol'], rule['port'], rule['direction'])
            created.append(rule_name)
        if len(created) > 0:
            #for name in created:
                #print(f"nova firewall rule: {name}")
            time.sleep(5)
            ctypes.windll.shell32.ShellExecuteW(None, "open", sys.executable, f'"{sys.argv[0]}" --no-elevate', None, 1)
            sys.exit()
        #else:
            #print("uz vsetky rules existuju")
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


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


class Networking:
    def __init__(self):
        self._send = None
        self.save = Saving()
        self._game_sock = None
        self._devices = {}
        self._self_address = socket.gethostbyname(socket.gethostname())
        #print(self._self_address)
        #print(get_local_ip())
        self._discovering = False
        self._nic = 0

        self._nick = None


        self._game_started = False
        # callbacky
        self.on_move_recieved = lambda x: None

        self.on_game_invite = lambda nick, uuid: None
        self.on_game_invite_rejected = lambda: None

        self.on_connect = lambda uuid: None
        self.on_disconnect = lambda text: None
        self.on_new_discovery = lambda devices: None

        self.no_devices_found = lambda cas: None

        self.on_online_game_start = lambda zacinajuci, nick: None
        #delete s.system()
        self._x_size = 7
        self._y_size = 6
        self._max_wins = 3

        self._tcp_recieving = False

        data = self.save.load_and_decrypt()

        self._uuid = data[0]
        self._nick = data[1]

        self._opponent_uuid = None
        self._opponent_conn = None

        self._is_server = False

        self._previous_send = 0
        self._previous_recv = 0
        self._previous_del = 0
        self._previous_device = 0
        self._recvs = {}

        _manage_firewall_rules()

    def get_uuid(self):
        a = 5
        #print(self._uuid)

    def set_nickname(self, nickname):
        self.save.update_nick(nickname)
        self._nick = nickname

    def get_nickname(self):
        return self._nick

    def get_devices(self):
        return self._devices

    def get_discovering(self):
        return self._discovering

    def set_game_settings(self, max_wins):
        self._max_wins = max_wins

    def get_game_settings(self):
        return self._x_size, self._y_size, self._max_wins

    def start_discovery(self):
        self._nic = 0
        self._previous_send = 0
        self._previous_recv = 0
        self._previous_del = 0
        self._recvs = {}
        self._discovering = True
        self._send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self._send.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        self._send.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)

        num = 0
        for i in netifaces.interfaces():
            if "Virtual" in i or "virtual" in i or "loop" in i or "Loop" in i or 2 not in netifaces.ifaddresses(
                    i).keys():
                if i not in ['vpn', 'Vpn', 'VPN']:
                    continue
            num += 1
            #print(i)
            j = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            j.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            j.bind(('', MPORT))
            #print(netifaces.ifaddresses(i)[2][0]['addr'])
            mreq = ip2bytes(MGROUP) + ip2bytes(netifaces.ifaddresses(i)[2][0]['addr'])  # tu musi byt presne zadana ipcka interfacu s inteom - bud ethernet alebo skor wifi
            j.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            j.settimeout(1)
            j.setblocking(False)
            self._recvs[j] = netifaces.ifaddresses(i)[2][0]['addr']
        if num == 0:
            raise ZeroDivisionError
        self._previous_device = time.time()
        #print('zacate vyhladavanie')

    # toto treba osetrit, aby pri vypnuti programu sa vykonalo spolocne so stop_tcp_listen
    #
    #
    def stop_discovery(self):
        self._send.close()
        self._discovering = False
        #print("ukonceny discovery")

    def discovery_tick(self):
        if not self._discovering:
            return
        current_time = time.time()
        if current_time - self._previous_send > 5:
            # posielanie hello do multicast group
            self._previous_send = current_time
            sprava = json.dumps(
                {
                    'app': 'connect43sa',
                    'nick': self._nick,
                    "type": "discovery",
                    "timestamp": int(time.time()),
                    "uuid": self._uuid,
                }
            ).encode()
            # print('send -', sprava)
            self._send.sendto(sprava, (MGROUP, MPORT))
        if current_time - self._previous_recv > 1:
            self._previous_recv = current_time
            ready_socks = select.select(list(self._recvs.keys()), [], [], 0)[0]
            if not ready_socks:
                self._nic += 1
            else:
                self._nic = 0
                for recv in ready_socks:
                    try:
                        data, addr = recv.recvfrom(1024)
                        message = json.loads(data.decode())
                        if message["app"] == "connect43sa" and message["type"] == "discovery" and message[
                            'uuid'] != self._uuid:
                            ip = addr[0]
                            if ip in self._devices:
                                if self._devices[ip]['timestamp'] == message['timestamp']:
                                    #print("skipnuty rovnaky timestamp")
                                    continue
                                self._devices[ip]['timestamp'] = int(time.time())
                                #print("zmeneny timestamp")
                            else:
                                x = int(time.time()) - message['timestamp']
                                self._devices[ip] = {
                                    'nick': message['nick'],
                                    'uuid': message['uuid'],
                                    'timestamp': int(time.time()),
                                    'last_ping': x if x >= 0 else 0,
                                    'from_ip': recv.getsockname()[0],
                                }
                                #print("pridane zar")
                            # print(f"sprava prijata: {message}")
                            self._previous_device = current_time
                        elif message["app"] == "connect43sa" and message["type"] == "accept" and message[
                            'uuid'] != self._uuid and message['target'] == self._uuid:
                            #print(f"prijata pozvanka: {message}")
                            self.handle_message(message, decoded=True)
                    except (socket.timeout, json.JSONDecodeError):
                        continue
            for ip in self._devices:
                last = int(time.time()) - self._devices[ip]['timestamp']
                if last < 0:
                    last = 0
                self._devices[ip]['last_ping'] = last
        if self._nic >= 30:
            self.no_devices_found(current_time - self._previous_device)
        if current_time - self._previous_del > 15:
            self._previous_del = current_time
            old_ips = [ip for ip, info in self._devices.items() if current_time - info['timestamp'] > 15]
            for ip in old_ips:
                del self._devices[ip]
                #print(f'vymazana stara ip: {ip}')
        return self._devices


    def check_tcp_messages(self):
        try:
            nic = 0
            #print("slucham")
            if self._is_server:
                if nic >= 45:
                    if self._opponent_conn is not None:
                        self._opponent_conn.close()
                    if self._game_sock is not None:
                        self._game_sock.close()
                    self._game_sock = None
                    self._game_started = False
                    self._tcp_recieving = False
                    self.on_disconnect("Hráč nebol k dosahu.")
                    #print("nic >= 45")
                    return
                if not self._opponent_conn:
                    try:
                        conn, addr = self._game_sock.accept()
                        conn.setblocking(False)
                        self._opponent_conn = conn
                        #print("Prijaté spojenie od:", addr)
                    except BlockingIOError:
                        # non-blocking socket - nič ešte neprišlo
                        #print('kaer29458341')
                        return
                    except socket.error as e:
                        print(f"TCP chyba pri prijímaní (accept): {e}")
                        return

                try:
                    data = self._opponent_conn.recv(1024)
                    if data:
                        self.handle_message(data)
                    if not data:
                        nic += 1
                        print(nic)
                except BlockingIOError:
                    #print('bfkdfoak123')
                    pass
                except socket.error as e:
                    print("TCP chyba pri prijímaní (server recv):", e)
            else:
                if nic >= 45:
                    self._game_sock.close()
                    self._game_sock = None
                    self._game_started = False
                    self._tcp_recieving = False
                    self.on_disconnect("Hráč nebol k dosahu.")
                    return
                try:
                    data = self._game_sock.recv(1024)
                    if data:
                        self.handle_message(data)
                    if not data:
                        nic += 1
                        #print(nic)
                except BlockingIOError:
                    #print('block335')
                    pass
                except socket.error as e:
                    print("TCP chyba pri prijímaní (klient recv):", e)
        except Exception as e:
            print("Neočakávaná výnimka:", e)


    # zapne sa pri prichode a vypne sa pri odchode z discovery/hry
    def start_tcp_listen(self, uuid):
        nick = None
        self._is_server = True
        self._opponent_uuid = uuid
        self._tcp_recieving = True
        self._game_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._game_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._game_sock.setblocking(False)
        for ip, info in self._devices.items():
            if info['uuid'] == self._opponent_uuid:
                self._self_address = info['from_ip']
                nick = info['nick']
                break
        try:
            #print(f"[SERVER] Pocuvam na: {self._self_address}:{PORT}")
            self._game_sock.bind((self._self_address, PORT))
        except OSError as e:
            print(f"Chyba pri nastavani posluchania: {e}")
            self._game_sock.close()
            raise RuntimeError
        self._game_sock.listen(1)
        self._game_started = True
        self._opponent_conn = None
        #print("hra bola zacata")
        self.on_online_game_start(True, nick)

    def stop_tcp_listen(self):
        self._tcp_recieving = False

    def connect_to_server(self, uuid_game):
        address = None
        nick = None
        for ip, info in self._devices.items():
            if info['uuid'] == uuid_game:
                address = ip
                nick = info['nick']
                break
        if not address:
            raise Exception("Zariadenie sa nenaslo")
        try:
            #print(f"[CLIENT] Pokus o pripojenie na: {address}:{PORT}")
            if self._game_sock is not None:
                #print("opa")
                self._game_sock.close()
            self._game_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._game_sock.connect((address, PORT))
            self._game_sock.setblocking(False)
            self._game_started = True
            self._is_server = False
            self.on_online_game_start(False, nick)
            #print("hra bola zacata")
            self._tcp_recieving = True
        except (socket.error, ConnectionRefusedError) as e:
            self._game_sock = None
            print(f"Nastala chyba pri pripajani: {e}")

    def handle_message(self, recv, decoded=False):
        #print("ahoj")
        if not decoded:
            message = json.loads(recv.decode())
        else:
            message = recv
        #print(message)
        if self._game_started:
            #print("hra zacata")
            if message['uuid'] != self._opponent_uuid and message['target'] != self._uuid:
                return
            else:
                action = message['type']
                if action == 'move':
                    self.handle_move(message)
                elif action == 'disconnect':
                    self.handle_disconnect(message)
                else:
                    return
        else:
            if 'uuid' not in message.keys() or message['uuid'] == self._uuid:
                pass
            else:
                action = message['type']
                if action == 'accept' and self._game_started is False:
                    self.handle_accept(message)
                elif action == 'disconnect':
                    self.handle_disconnect(message)
                else:
                    print("Invalid message type")
                """
                elif action == 'move':
                    self.handle_move(message)
                """

    def handle_accept(self, message):
        if message['confirm'] == 'confirm':
            self.on_game_invite(message['nick'],
                                message['uuid'])  # tu si pouzivatel aj nastavi nastavenia hry, ze ako velka bude
        elif message['confirm'] == 'confirmed':
            self.on_connect(message['uuid'])
        elif message['confirm'] == 'started':
            self.connect_to_server(message['uuid'])
        elif message['confirm'] == 'rejected':
            self.on_game_invite_rejected()

    def handle_disconnect(self, message):
        if self._game_sock is not None:
            self._game_sock.close()
            self._game_sock = None
            self._game_started = False
            self.on_disconnect(message['text'])

    def handle_move(self, message):
        x = message['x']
        #print("prijaty tah", message)
        self.on_move_recieved(x)

    # Poslanie pozvanky na hru – preposlanie do 2. zariadenia, nepovinny 2. parameter - 0 poslat pozvanku, 1 potvrdzujem poznamku, 2 odmietnuta pozvanka
    def game_accept(self, target_uuid, max_wins=3, accept=0):
        try:
            if accept == 0:
                confirm = 'confirm'
                # self.set_game_settings(max_wins)
                message = {'app': 'connect43sa', 'type': 'accept', 'uuid': self._uuid, 'target': target_uuid,
                           'confirm': confirm, 'max_wins': max_wins, 'nick': self._nick}
            elif accept == 1:
                confirm = 'confirmed'
                message = {'app': 'connect43sa', 'type': 'accept', 'uuid': self._uuid, 'target': target_uuid,
                           'confirm': confirm}
                self._opponent_uuid = target_uuid
            elif accept == 3:
                confirm = 'started'
                message = {'app': 'connect43sa', 'type': 'accept', 'uuid': self._uuid, 'target': target_uuid,
                           'confirm': confirm}
            else:
                confirm = 'rejected'
                # self.set_game_settings(max_wins)
                message = {'app': 'connect43sa', 'type': 'accept', 'uuid': self._uuid, 'target': target_uuid,
                           'confirm': confirm}
            self._send.sendto(json.dumps(message).encode(), (MGROUP, MPORT))
        except (socket.error, ConnectionRefusedError) as e:
            print(e)
            raise Exception(f"Pozvanku sa nepodarilo odoslat. {e}")

    def send_move(self, x):
        if not self._game_sock:
            raise Exception("nie je aktivne spojenie")
        try:
            message = {'app': 'connect43sa', 'type': 'move', 'uuid': self._uuid, 'x': x, 'target': self._opponent_uuid}
            if self._opponent_conn:
                send_message(message, self._opponent_conn)
                #print("opp")
            else:
                send_message(message, self._game_sock)
                #print("game")
        except socket.error:
            try:
                if self._opponent_conn:
                    self._opponent_conn.close()
            except:
                #print("opp nejdze")
                pass
            try:
                if self._game_sock:
                    self._game_sock.close()
            except:
                #print("game nejdze")
                pass
            #print("com som tu")
            self._opponent_conn = None
            self._game_sock = None
            self._game_started = False
            try:
                self.on_disconnect("Nastala chyba pri odosielaní ťahu.")
            except:
                pass

    def send_disconnect(self, text="Nastala chyba, hra skončila."):
        try:
            message = {'app': 'connect43sa', 'type': 'disconnect', 'uuid': self._uuid, 'text': text}
            if self._opponent_conn:
                send_message(message, self._opponent_conn)
            else:
                send_message(message, self._game_sock)
        except socket.error:
            #print("coska wrong")
            try:
                if self._opponent_conn:

                    self._opponent_conn.close()
            except:
                pass
            try:
                if self._game_sock:
                    self._game_sock.close()
            except:
                pass
            self._opponent_conn = None
            self._game_sock = None
            self._game_started = False



if __name__ == "__main__":
    net = Networking()
    try:
        net.get_uuid()
        # print(net.handle_message(b'{"type": "disconnect"}'))
        net.start_discovery()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        #print("KeyboardInterrupt")
        net.stop_discovery()
        net.stop_tcp_listen()
        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)

# TCP Error:  [WinError 10057] A request to send or receive data was disallowed because the socket is not connected and (when sending on a datagram socket using a sendto call) no address was supplied
# Accept Error: Accept Error:  timed out
# timed out
# TCP klient listener ukončený.
