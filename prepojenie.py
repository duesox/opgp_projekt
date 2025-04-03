import socket
import select

PORT = 40337
MPORT = 40338


def ip2bytes(addr):
    return socket.inet_aton(addr)


class Networking:
    def __init__(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._multicast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._multicast.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._multicast.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        self._multicast.bind(('224.0.0.123', MPORT))
        mreq = ip2bytes('224.0.0.123') + ip2bytes('0.0.0.0')
        self._multicast.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self._sprava = None
        self._self_address = None
        self._address = None
        self._client_sock = None
        self._clients = []

    # ked sa najdu 2 zariadenia na sieti
    def network_discovery(self):
        self._multicast.bind(('', MPORT))
        self._multicast.listen(1)
        while True:  # skor by som toto vymazal a spravil periodicke spustanie funkcie
            self._client_sock, self._address = self._multicast.accept()
            for zaznam in self._clients:
                if zaznam[1] != self._address or len(self._clients) == 0:
                    self._clients.append([None, self._address])
            print("nove pripojenie")
            self._sprava = self._sock.recv(1024)
            self._sprava = self._sprava.decode()

    # prijatie spravy z 2. zariadenia
    def net_accept(self):
        self._sock.bind(('', PORT))
        self._sock.listen(1)
        x = select.select(self._clients, [], [], 0)[0]
        for client_sock in x:

            recieved = client_sock.recv(1024)
            if recieved:
                if "accept" in self._sprava:
                    self._clients = [client_sock]
                    self._self_address = self._client_sock.getsockname()[0]
                    self.game_accept(1)
                    return 0
                elif "disconnect" in self._sprava:
                    self._sock.close()
                    self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    print("odpojene")
                    return 1
                elif "move" in self._sprava:
                    move = self._sprava.split('-')
                    return 2, move[0], move[1]

    # Prijatie pozvanky na hru – preposlanie do 2. zariadenia
    def game_accept(self, adresa, what=0):
        self._accept_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._accept_sock.connect((adresa, PORT))
        if what == 0:
            self._accept_sock.send(self._self_address.encode() + b'-accept')
        else:
            self._accept_sock.send(self._self_address.encode() + b'-accepted')
