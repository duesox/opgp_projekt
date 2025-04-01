import socket
import select


class Networking:
    def __init__(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._PORT = 40337

    def network_discovery(self):
        self._sock.bind(('', self._PORT))
        self._sock.listen(1)
        return self._sock
