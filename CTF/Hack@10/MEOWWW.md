<img width="605" height="547" alt="image" src="https://github.com/user-attachments/assets/c251594b-4378-47e8-9246-2959d2ef132d" />

<img width="1600" height="1598" alt="image" src="https://github.com/user-attachments/assets/00b4f6c7-d7a1-43db-83e7-1a6da9c0cd8d" />

# **Step 1: Initial Reconnaissance**

The provided file is a JPEG image of a cat. Initial analysis with standard tools (`file`, `exiftool`) confirmed it is a standard JFIF/JPEG image.

<img width="696" height="551" alt="image" src="https://github.com/user-attachments/assets/e5d049a1-71b0-48bb-b837-a87ddc10ab02" />

Using [Aperi'Solve - Steganography Analysis](https://www.aperisolve.com/) and `strings`, several suspicious patterns were noted:

1.  High entropy strings that looked like Base64 fragments (e.g., `ZW5Q...`) were visible, suggesting embedded data.

2. **Binwalk r**eported a warning that one or more files failed to extract, hinting that data was appended or embedded in a way standard carvers might miss.

<img width="1347" height="133" alt="image" src="https://github.com/user-attachments/assets/8f0a8a2c-2ff7-4b1a-b002-8ca72461ed36" />

1. **Steghide:** Failed to extract data without a passphrase.

<img width="1387" height="118" alt="image" src="https://github.com/user-attachments/assets/48ce5628-e0a2-4a1b-bea4-95f21f96fb6d" />

# Password Bruteforcing

Since `steghide` was suspected but the passphrase was unknown, I used **Stegseek** to brute-force the image against the `rockyou.txt` wordlist.

<img width="1842" height="202" alt="image" src="https://github.com/user-attachments/assets/3afc5cf4-0748-4806-92ef-53f7ebf99cf5" />

- **Passphrase found:** `hidden`
- **Extracted file:** `chal.ps1` (original filename)

# PowerShell Analysis

The extracted file, `chal.ps1`, contained a heavily obfuscated PowerShell one-liner:

<img width="1895" height="123" alt="image" src="https://github.com/user-attachments/assets/44adca16-4786-494f-9300-b186c2fe4cdb" />

**De-obfuscation Breakdown:**

1. **Base64 String:** `UzF19/UJV7BVUMpITM42NKguMCg3LopPMU42SDGuVQIA`
2. **Compression:** The script uses `DeflateStream` to decompress the Base64-decoded bytes.
3. **Execution:** The trailing pipe `| & ( $eNV:cOmSPEc[4,15,25]-JOin'')` resolves to `Invoke-Expression` (`IEX`), which attempts to run the decoded output.

# **Decoding the Payload**

To safely view the payload without executing it, I used a Python one-liner to decode the Base64 and decompress the raw Deflate stream.

<img width="1891" height="118" alt="image" src="https://github.com/user-attachments/assets/ca9a770f-af7f-4c97-a1a2-cf9b4256d2cf" />

```bash
Flag: hack10{p0w3r_d3c0d3}
```
