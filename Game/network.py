import socket
socket.setdefaulttimeout(6)
import pickle


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def setup(self, addr):
        self.addr = addr

    def connect(self, playername, skin):
        try:
            self.client.connect(self.addr)
        except:
            print("[ERROR] Could not connect to server.")
            exit()
        
        self.client.send(pickle.dumps((playername, skin)))
        result = self.client.recv(8)
        return int(result.decode())

    def disconnect(self):
        self.client.close()

    def send(self, data, pick=False):
        try:
            if pick:
                self.client.send(pickle.dumps(data))
            else:
                self.client.send(str.encode(data))
            reply = self.client.recv(2048*4)
            try:
                reply = pickle.loads(reply)
            except Exception as e:
                print(e)

            return reply
        except socket.error as e:
            print(e)
