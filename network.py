import socket
import pickle


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = ("192.168.1.194", 8080)

    def connect(self, playername):
        self.client.connect(self.addr)
        self.client.send(str.encode(playername))
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
