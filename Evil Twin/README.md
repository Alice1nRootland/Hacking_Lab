# 📡 Evil Twin Attack Awareness & Tutorial (Airgeddon Edition)

**Author:** Faez  
**Category:** Wireless Security / Awareness  
**Difficulty:** Beginner to Intermediate  
**Platform:** Kali Linux + Airgeddon

---

## 🧠 Overview

This repository raises awareness about **Evil Twin attacks** — a wireless threat where attackers create a fake access point to trick users into connecting. Using **Airgeddon**, we demonstrate how easily such attacks can be launched and how users can protect themselves.

This repo includes:
- A beginner-friendly explanation of Evil Twin attacks  
- A hands-on tutorial using Airgeddon  
- Screenshots of each step  
- Mitigation tips for users and network defenders

---

## 📖 What Is an Evil Twin Attack?

An **Evil Twin** is a rogue Wi-Fi access point that impersonates a legitimate one. Once victims connect, attackers can:
- Serve fake login portals  
- Capture credentials  
- Perform man-in-the-middle attacks

---

## 🛠️ Tools Used

- **Kali Linux**  
- **Airgeddon** – automated wireless attack framework  
- **Compatible Wi-Fi adapter** (supports monitor mode and packet injection)

---

## 🚀 Tutorial: Evil Twin Setup with Airgeddon

### 1. Clone and Run Airgeddon

```bash
git clone https://github.com/v1s1t0r1sh3r3/airgeddon.git
cd airgeddon
sudo bash airgeddon.sh
