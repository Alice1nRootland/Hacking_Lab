# 🧠 Reminiscent – Memory Forensics CTF Writeup

**Challenge:** Reminiscent  
**Platform:** Hack The Box (HTB)  
**Category:** Memory Forensics  
**Author:** Faez  
**Flag:** `FLAG{reflective_injection_mastery}`

---

## 🧩 Challenge Overview

This challenge simulates a real-world fileless malware attack triggered by a malicious email. We were provided with a Windows memory dump and a suspicious `.eml` file. The goal was to analyze the memory, trace the infection chain, decode the payload, and extract the flag.

---

## 🗂️ Files Provided

- `flounder-pc-memdump.elf` – Memory dump of the target machine  
- `imageinfo.txt` – Suggested Volatility profiles  
- `Resume.eml` – Suspicious email attachment

---

## 🔍 Step-by-Step Analysis

### 1. Profile Identification

Using Volatility’s `imageinfo`, we identified the best profile:

```bash
vol.py -f flounder-pc-memdump.elf imageinfo
