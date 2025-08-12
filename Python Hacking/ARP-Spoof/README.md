# 🧠 ARP Spoofing Educational Report

This repository contains a beginner-friendly educational overview and demonstration of ARP spoofing using Python and Scapy. It includes:

- A formal writeup explaining ARP spoofing
- Python scripts for spoofing and verification
- Instructions for setup and testing
- Guidance for ethical use

## 📄 Contents

- `report.md`: Formal educational writeup
- `arpspoofer.py`: ARP spoofing script
- `malarp.py`: ARP table inspection script
- `assets/`: Optional screenshots or diagrams

## 🛠️ Requirements

- Python 3
- Scapy library (`pip3 install scapy`)
- Root privileges to run the script

## ▶️ Running the Spoofer

```bash
sudo python3 arpspoofer.py <router_ip> <target_ip>
