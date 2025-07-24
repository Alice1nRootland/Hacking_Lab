# 🕵️‍♂️ ExifTool Steganography Demo – OSINT Walkthrough

This repository contains a simple yet powerful demonstration of how to hide and extract secret messages from JPEG images using `exiftool` on Kali Linux. The technique is useful in OSINT investigations, CTF challenges, and digital forensics.

## 📄 Demo PDF

## 🛠️ Tools Used
- Kali Linux
- `exiftool`

## 🧪 What You'll Learn
- How to embed a hidden message in an image
- How to extract metadata using `exiftool`
- How steganography can be used in real-world investigations

## 📸 Sample Command
```bash
exiftool -comment='I janji I ada you sorang je' github.com.jpg
exiftool -v github.com.jpg

