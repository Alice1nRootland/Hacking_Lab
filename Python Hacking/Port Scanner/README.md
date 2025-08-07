# 🔍 Python Port Scanner — Educational Tool for Network Reconnaissance

> ⚠️ **Disclaimer**  
This script is intended **solely for educational purposes**. Do **not** use it to scan systems you do not own or have explicit permission to test. Unauthorized scanning may violate laws and ethical guidelines. Always respect the boundaries of responsible cybersecurity practice.

---

## 📌 Overview

This Python script performs a basic **TCP port scan** on a target IP or domain, identifying open ports and attempting to grab service banners. It’s a lightweight alternative to tools like Nmap, designed to help beginners understand how port scanning works under the hood.

---

## 🧠 Features

- Accepts single or multiple targets
- Resolves domain names to IPs
- Scans ports 1–499
- Attempts banner grabbing for open ports
- Handles timeouts and connection errors gracefully

---

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Alice1nRootland/python-port-scanner.git
cd python-port-scanner
. Install Dependencies
bash
pip install -r requirements.txt
💻 Usage
Run the script:

bash
python3 scanner.py
Example input:

[+] Enter Target/s to Scan (Split multiple targets with ,): scanme.nmap.org,example.com
Example output:

[-0 Scanning Target] scanme.nmap.org
[+] Open Port 22 : SSH-2.0-OpenSSH_7.6p1 Ubuntu-4ubuntu0.3
[+] Open Port 80 : Apache/2.4.29 (Ubuntu)
...
📖 Code Breakdown
🔹 check_ip(ip)
Resolves domain names to IP addresses using IPy and socket.gethostbyname.

🔹 scan_port(ipaddress, port)
Attempts to connect to each port. If successful, tries to grab a service banner.

🔹 get_banner(s)
Reads up to 1024 bytes from the socket to identify the service.

🔹 scan(target)
Iterates through ports 1–499 for each target.
Contribute
Feel free to fork, improve, or adapt this script for your own learning. Pull requests are welcome!

🧠 Educational Value
This script is ideal for:

Cybersecurity students learning about TCP/IP
CTF players building custom tools
Educators explaining port scanning mechanics
Beginners transitioning from GUI tools to Python scripting
