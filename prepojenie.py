import socket
import select


class Networking:
    def __init__(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._PORT = 40337
        self._sprava = None
        self._self_address = None
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
    def game_accept(self, what=0):
        if what == 0:
            self._client_sock.send(self._self_address.encode() + b'-accept')
        else:
            self._client_sock.send(self._self_address.encode() + b'-accepted')

