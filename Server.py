import socket
import os
import threading
import datetime
import json

SOCKET_PORT = int(os.getenv('PORT', 1234))
SOCKET_BIND = os.getenv('BIND', "0.0.0.0")


class Client:
    socket = None
    rfile = None
    address = None
    name = None
    thread = None

    def __init__(self, socket, address) -> None:
        self.socket = socket
        self.address = address
        self.rfile = socket.makefile()
        self.name = address[0] + ":" + str(address[1])
        self.thread = threading.Thread(target=self.handle)
        self.thread.daemon = True
        self.thread.start()


    def handle(self):
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " [client: " + self.name + "] connected!")
        while True:
            try:
                content = self.rfile.readline()
                data = json.loads(content)
                if (data.get("method") == "setUsername"):
                    self.name = data.get("data")
                elif (data.get("method") == "broadcast"):
                    print(data.get("timestamp") + " [client: " + data.get(
                        "source") + "] sent a message to all users: " + data.get("data"))
                    for x in clients:
                        if x.name != self.name:
                            x.send({"method": "broadcast", "source": self.name, "data": data.get("data")})
                elif (data.get("method") == "private"):
                    flag = False
                    print(data.get("timestamp") + " [client: " + data.get("source") + "] sent private message to: " + data.get("destination") + " with the following message: " + data.get("data"))
                    for x in clients:
                        if x.name == data.get("destination"):
                            x.send({"method": "private", "source": self.name, "data": data.get("data")})
                            flag = True
                    for x in clients:
                        if x.name == data.get("source") and flag == False:
                            x.send({"method": "private", "source": "[Server]", "data": "Client doesn't exist!"})
            except:
                print("Error: bad request")
        self.close()

    def send(self, data):
        format = bytes(json.dumps(data) + "\n", "UTF-8")
        self.socket.send(format)

    def close(self):
        with server_lock:
            print("[client: " + self.name + "] is leaving")
            self.socket.close()
            clients.remove(self)
            print("[client: " + self.name + "] is leaving")


print("[system] Starting server on port: " + str(SOCKET_PORT))
clients = set()
server_lock = threading.Lock()
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SOCKET_BIND, SOCKET_PORT))
server_socket.listen(10)
print("[system] Server successfully started on port: " + str(SOCKET_PORT))

while True:
    try:
        socket, address = server_socket.accept()

        with server_lock:
            client = Client(socket, address)
            clients.add(client)

    except KeyboardInterrupt:
        break
    except:
        pass
print("[system] Server shutting down")
for x in list(clients):
    x.close()
server_socket.close()
print("[system] Server successfully shutted down")


