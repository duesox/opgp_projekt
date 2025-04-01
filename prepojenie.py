import socket
import select


class Networking:
    def __init__(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._PORT = 40337
        self._sprava = None
        self._klient = None
        self._address = None

    # ked sa najdu 2 zariadenia na sieti
    def network_discovery(self):
        self._sock.bind(('', self._PORT))
        self._sock.listen(1)
        clients = []
        while True:
            self._klient, self._address = self._sock.accept()
            clients.append(self._klient)
            print("nove pripojenie")
            self._sprava = self._klient.recv(1024)
            self._sprava = self._sprava.decode()

    # ked sa dostane sprava z 2. zariadenia
    def net_accept(self):
        self._sprava = self._klient.recv(1024).decode()
        if "accepted" in self._sprava:
            return 0
        elif "disconnect" in self._sprava:
            return 1
        elif "move" in self._sprava:
            return 2, "move"



        self._sock.close()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("odpojene")

    #
    def game_accept(self):
        self._klient.send(b''+self._address[0]+b'-accepted')

