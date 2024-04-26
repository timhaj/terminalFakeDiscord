import datetime
import socket
import os
import threading
import json
import sys

SOCKET_PORT = int(os.getenv('PORT', 1234))
SOCKET_HOST = os.getenv('HOST', "127.0.0.1")
username = None

def inputUsername():
    global username
    try:
        while username is None:
            inp = input("[System] Enter your name: ")
            if inp.isalpha():
                username = inp
    except KeyboardInterrupt:
        print("Error: Keyboard Interrupt")
        sys.exit()


def receiver(socket):
    rfile = socket.makefile()
    while True:
        try:
            raw = rfile.readline()
            if not raw:
                continue
            data = json.loads(raw)
            if data.get("method") == "broadcast" or data.get("method") == "private":
                print("\n[" + data.get("source") + "] " + data.get("data"))
                print("[" + username + "] ", end="", flush=True)
        except Exception:
            print("Error: received bad message")
            pass


def send(data):
    format = bytes(json.dumps(data) + "\n", "UTF-8")
    socket.send(format)


def command(data):
    cmd, *args = data[1:].split(" ")
    if cmd == "help":
        print("Commands:\n\t/help -> Display the help menu\n\t/msg <username> <message> -> Send a private message to a specific username (has to be connected!)\n\t<message> -> Sends a message to all connected users (broadcast)")
    elif cmd == "msg":
        send({"method": "private", "destination": args[0], "data": " ".join(args[1:]), "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "source": username})
    else:
        print("[system] Error: Invalid command. Try /help to display all available commands.")


inputUsername()

while True:
    try:
        print("[system] connecting to chat server ... ", end="", flush=True)
        socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connected = False
        while connected is False:
            try:
                socket.connect((SOCKET_HOST, SOCKET_PORT))
                connected = True
                send({"method": "setUsername", "data": username})
            except Exception:
                print("Error: cannot set username")
        print("\n[system] Successfully established a connection. ")
        thread = threading.Thread(target=receiver, args=(socket,))
        thread.daemon = True
        thread.start()
        while True:
            try:
                print("[" + username + "] ", end="", flush=True)
                inp = input("")
                if inp == "":
                    continue
                elif inp[0] == "/":
                    command(inp)
                else:
                    send({"method": "broadcast", "data": inp, "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "source": username})
            except Exception as e:
                print("Error: bad input")
                break
    except KeyboardInterrupt:
        print("Error: Stopping and exiting")
        sys.exit()
