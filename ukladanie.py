from cryptography.fernet import Fernet
from platformdirs import user_data_dir
import os
import uuid

APP_NAME = "Connect4"
AUTHOR = "C4kaci"
DATA_DIR = user_data_dir(APP_NAME, AUTHOR)
KEY = b'WzTSykkLOrTK4eW3BsqfdD2K3lNQqFwX9XKqCRJ3gx0='

CONF_FILE = os.path.join(DATA_DIR, 'conf.secure')





class Saving:
    def __init__(self):
        self._uuid = None
        self._nick = None
        self._score = 0

        if not os.path.exists(CONF_FILE):
            os.makedirs(DATA_DIR, exist_ok=True)
            default_data = ["null", "null", 0]
            self.encrypt_and_save(default_data)
            #print("Konfiguracny subor vytvoreny.")
        if os.path.exists(CONF_FILE):
            udaje = self.load_and_decrypt()
            self._uuid = udaje[0]
            self._nick = udaje[1]
            self._score = udaje[2]
            if self._uuid == "null":
                self._uuid = str(uuid.uuid4())
                udaje[0] = self._uuid
                self.encrypt_and_save(udaje)
            if self._nick == "null":
                self._nick = "user_"+self._uuid[:6]
                udaje[1] = self._nick
                self.encrypt_and_save(udaje)
            #print(udaje)

    def encrypt_and_save(self, data):
        fernet = Fernet(KEY)
        str_data = [str(d) for d in data]
        encrypted = fernet.encrypt("\n".join(str_data).encode())
        with open(CONF_FILE, "wb") as f:
            f.write(encrypted)


    def load_and_decrypt(self):
        fernet = Fernet(KEY)
        with open(CONF_FILE, "rb") as f:
            encrypted = f.read()
        return fernet.decrypt(encrypted).decode().strip().split("\n")

    def update_nick(self, new_nick):
        data = self.load_and_decrypt()
        data[1] = new_nick
        self.encrypt_and_save(data)
        self._nick = new_nick