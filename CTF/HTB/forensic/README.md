# 🧠 Reminiscent – Memory Forensics CTF Writeup

**Challenge:** Reminiscent  
**Platform:** Hack The Box (HTB)  
**Category:** Memory Forensics  
**Author:** Faez  
**Flag:** `HTB{$_j0G_y0uR_M3m0rY_$}`

---

## 🧩 Challenge Overview

This challenge simulates a real-world fileless malware attack triggered by a malicious email. We were provided with a Windows memory dump and a suspicious `.eml` file. The goal was to analyze the memory, trace the infection chain, decode the payload, and extract the flag.

---

## 🗂️ Files Provided

- `flounder-pc-memdump.elf` – Memory dump of the target machine  
- `imageinfo.txt` – Suggested Volatility profiles  
- `Resume.eml` – Suspicious email attachment




