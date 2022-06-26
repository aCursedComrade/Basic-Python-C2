cd /Compiled

# For Linux
pyinstaller --clean -F -c -n linux-server ../Scripts/sshserver.py && pyinstaller --clean -F -c -n linux-agent ../Scripts/agent.py

# For Windows
wine pyinstaller.exe --clean -F -c -n windows-server ../Scripts/sshserver.py && wine pyinstaller.exe --clean -F -c -n windows-agent ../Scripts/agent.py
