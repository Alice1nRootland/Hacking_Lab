# 🕵️‍♂️ ExifTool Steganography Demo – OSINT Walkthrough

## 📌 Introduction

Steganography is the practice of hiding information within other non-secret data. In this demo, we use `exiftool` on Kali Linux to embed a secret message inside a JPEG image’s metadata and retrieve it later. This technique is often used in OSINT investigations, CTF challenges, and digital forensics.

---

## 🛠️ Tools Required

- Kali Linux (or any Linux distro with `exiftool`)
- A JPEG image
- Terminal access

---

## 🧪 Step-by-Step Demo

### 🔹 Step 1: Embed a Secret Message

Use `exiftool` to insert a comment into the image metadata:

```bash
exiftool -comment='I janji I ada you sorang je' github.com.jpg

