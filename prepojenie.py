import socket
import select


class Networking:
    def __init__(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._PORT = 40337
        self._sprava = None
        self._sock = None
        self._address = None
        self._client_sock = None
        self._clients = []

    # ked sa najdu 2 zariadenia na sieti
    def network_discovery(self):
        self._sock.bind(('', self._PORT))
        self._sock.listen(1)
        while True:
            self._client_sock, self._address = self._sock.accept()
            self._clients.append(self._client_sock)
            print("nove pripojenie")
            self._sprava = self._sock.recv(1024)
            self._sprava = self._sprava.decode()

    # prijatie spravy z 2. zariadenia
    def net_accept(self):
        x = select.select([self._clients], [], [], 0)[0]
        if x:
            self._sprava = self._sock.recv(1024)
            if "accept" in self._sprava:
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
    def game_accept(self):
        self._sock.send(self._address[0]+b'-accept')
