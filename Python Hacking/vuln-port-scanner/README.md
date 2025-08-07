# 🛡️ Vulnerability Port Scanner — Banner Matching Tool for Educational Use

> ⚠️ **Disclaimer**  
This tool is intended **solely for educational purposes**. Do **not** use it to scan systems you do not own or have explicit permission to test. Unauthorized scanning may violate laws and ethical guidelines. Always respect responsible cybersecurity practices.

---

## 📌 Overview

This Python-based scanner performs a TCP port scan and checks for known vulnerable service banners. It’s designed to help students understand how banner grabbing and vulnerability matching works in real-world reconnaissance.

---

## 🧠 Features

- Scans first N ports (default: 500)
- Resolves domain names to IPs
- Grabs service banners from open ports
- Matches banners against a known vulnerable list
- Modular design using classes

---

Usage
Make sure all files are in the same directory:

portscanner.py
vulnscan.py
vulbanner.txt

Then run:

bash
python3 vulnscan.py
Example input:

[+] * Enter Target To Scan For Vulnerable Open Ports: scanme.nmap.org
[+] * Enter Amount Of Ports You Want To Scan(500 - first 500 ports): 500
[+] * Enter Path To The File With Vulnerable Softwares: vulbanner.txt
Example output:

[!!] VULNERABLE BANNER: "SSH-2.0-OpenSSH_5.3p1 Debian-3ubuntu7.1" ON PORT: 22

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Alice1nRootland/vuln-port-scanner.git
cd vuln-port-scanner
