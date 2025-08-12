# 🕵️‍♂️ Python Keylogger (Educational Use Only)

This project demonstrates a simple Python-based keylogger for educational and ethical hacking purposes. It captures keystrokes using the `pynput` library and stores them in a hidden log file. The goal is to understand how input monitoring works and how attackers might conceal their tools.

> ⚠️ **Disclaimer**: This tool is intended for learning only. Do not run it on systems you do not own or have explicit permission to test.

---

## 📌 Features

- ✅ Captures all keystrokes using `pynput`
- 📁 Saves logs to a hidden file:
  - On Windows: `%APPDATA%\keylog.txt`
  - On Linux/macOS: `./.keylog.txt`
- 🕶️ Runs silently in the background
- 🧠 Easy to read and modify for beginners

---

## 🚀 Getting Started

### 1. Install Dependencies

```bash
pip install pynput
