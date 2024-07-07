## Simple script that scans for available machines with ```tailscale status``` and creates an SFTP connection.

### tailssh Install
1. Download the script
2. Install python3
3. run the script :)
4. (optional Linux) add an alias ```echo "alias tailsftp='python3 ~/tailsftp.py'" >> ~/.bashrc``` then reload ```source ~/.bashrc``` now you only have to type tailsftp
5. (optional Windows) type ```notepad $PROFILE``` into you're powershell an add this to you're file:
```
function tailsftp {
    python "C:\path\to\the\script\tailsftp.py"
}
```
