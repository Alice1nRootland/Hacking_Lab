# 🔍 pass-sniffer.py — HTTP Credential Sniffer

A lightweight Python script that captures and extracts login credentials from unencrypted HTTP traffic using Scapy and regex. Designed for educational use in cybersecurity labs, CTF challenges, and network analysis.

---

## 🎯 Objective

This tool demonstrates how login credentials can be intercepted over insecure HTTP connections. It helps learners understand packet sniffing, regex-based data extraction, and the importance of encryption in web applications.

---

## 🧰 Requirements

- Python 3.x
- Scapy library
📦 Usage
Run the script with root privileges:

bash
sudo python3 pass-sniffer.py

If credentials are found in HTTP traffic:

[+] Potential Credentials Found:
    → username=admin
    → password=123456
    
🧪 How It Works
Sniffs TCP packets on the specified interface.

Filters for HTTP traffic (port 80).

Extracts raw payload from TCP layer.

Searches for known login field names using regex.

Prints and decodes credentials if both username and password are found.

📘 Educational Purpose
This project is intended for:

✅ Cybersecurity education

✅ CTF competitions

✅ Authorized penetration testing

⚠️ Do not use this tool on networks you do not own or have explicit permission to test. Unauthorized use is illegal and unethical.

📚 Suggested Extensions
🔐 Add HTTPS interception via mitmproxy

📄 Log credentials to file

🧰 Modularize with CLI options

🧪 Add ARP spoofing for full MITM setup

### ✅ Install Scapy
```bash
pip3 install scapy
