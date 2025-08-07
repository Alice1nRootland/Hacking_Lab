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
