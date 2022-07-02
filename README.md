# Basic-Python-C2

A basic command and control system made on top of SSH protocol with Python. This project is merely a follow along of Joe Helle's ([@TheMayor](https://twitter.com/joehelle)) simple [video guide](https://youtu.be/iP7eFbZPgss) for me to tinker around with. Strictly for educational purposes.

Compiled binaries (64 bit) are made with PyInstaller.

### Currently experimenting on:
- File transfers
- Handling multiple agents
- General improvements/features

### Notes:
Experimenting on reversing current server and agent code for a better outcome. Currently `server.py` host a `paramiko SSH Server` which provides similar services as a ordinary SSH service. Current goal is to send the "stub server" instead of `paramiko SSH client` as the payload with `agent.py`, so that a rogue SSH server can be set up on the other end.
