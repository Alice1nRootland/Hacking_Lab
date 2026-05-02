<img width="881" height="633" alt="image" src="https://github.com/user-attachments/assets/c80c44fc-3125-4346-bd2f-e35ba0803bc8" />

# Challenge Write‑Up: *Layoffs Phishing Document Analysis*

## Challenge Overview

Our SOC identified multiple phishing emails claiming to contain a document about an upcoming round of company layoffs. Each email included a link to:

```
http://diagnostic.htb/layoffs.doc
```

Although DNS resolution for `diagnostic.htb` had stopped, the server was still accessible via a provided Docker host. The goal was to analyze the malicious document and determine what it was doing — ultimately extracting the flag.

## Step 1: Downloading and Identifying the File

<img width="1093" height="232" alt="image" src="https://github.com/user-attachments/assets/689c483c-3e7f-42f2-8b60-20a3e487928e" />

The document was downloaded directly from the server:

```bash
curl http://diagnostic.htb:34387/layoffs.doc -o layoffs.doc
```

Checking the file type:

```bash
file layoffs.doc
```

**Result:**

```
Zip archivedata
```

This indicates the file is actually a **DOCX file**, which is a ZIP archive containing XML files.

## Step 2: Extracting the Document Contents

The document was unzipped for inspection:

<img width="580" height="367" alt="image" src="https://github.com/user-attachments/assets/5e0af4b0-e6c6-4053-9028-755e0b0e13e6" />

```sql
unzip layoffs.doc -d layoffs
tree layoffs
```

Key files of interest:

`word/document.xml`

`word/_rels/document.xml.rels`

`word/settings.xml`

These files commonly contain embedded links, macros, or exploit payloads.

## Step 3: Finding the Malicious Payload

Upon inspection, the document contained a malicious **`ms-msdt:` URL**, a known attack vector used in the **Follina (CVE‑2022‑30190)** vulnerability.

This payload included an **obfuscated PowerShell command** encoded in Base64.

<img width="1107" height="663" alt="image" src="https://github.com/user-attachments/assets/3d2841f7-07f5-4796-a80c-5d3a5b1bf8d1" />

## Step 4: Decoding the Base64 Payload (Safely)

The Base64 string was decoded **without executing it**:

<img width="1112" height="210" alt="image" src="https://github.com/user-attachments/assets/aa94b45d-7d4b-44df-a0f0-80d53052c97e" />

## Step 5: Understanding the Obfuscation

The script dynamically builds a filename using PowerShell’s string formatting:

```powershell
"{7}{1}{6}{8}{5}{3}{2}{4}{0}"
```

Reassembling the string reveals:

```
HTB{msDt_4s_A_pr0toC0l_h4nDl3r...sE3Ms_b4D}.exe
```

This filename contains the **CTF flag**.
