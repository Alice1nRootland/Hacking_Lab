<img width="621" height="591" alt="image" src="https://github.com/user-attachments/assets/6dbdb51f-366f-412e-880a-81882e638186" />

#### Environment Setup & Volatility 3 Installation

To analyze the physical memory capture accurately, Volatility 3 was installed inside a Python virtual environment on an analysis workstation running Kali Linux to prevent dependency conflicts with system-wide packages.

<img width="1492" height="331" alt="image" src="https://github.com/user-attachments/assets/29f62889-1f7f-40bf-b972-dcf8a6dff2cb" />


#### Memory Forensics & Profile Triage

Before pivoting to specialized extraction plugins, the operating system profile and layout boundaries of the image were established using the `windows.info` plugin.

```jsx
vol -f WINDOWS-MEM.mem windows.info
```

<img width="1392" height="421" alt="image" src="https://github.com/user-attachments/assets/2108e870-6a35-4bf0-885a-e3c02ec1ab52" />


#### Profile Artifacts:

- **Operating System:** Windows 10 (Major/Minor version: 15.19041)
- **Architecture:** 64-bit (Intel32e)
- **Capture Timestamp:** 2026-04-07 16:13:42 UTC

#### Process Triage & Threat Analysis

The problem statement specified that the suspect was actively using a text editor during the compromise. To identify the target execution process and review general system behavior, a full process listing was generated.

```jsx
vol -f WINDOWS-MEM.mem windows.pslist
```

<img width="1230" height="762" alt="image" src="https://github.com/user-attachments/assets/234363e5-b75f-4ba8-9110-0cdba1129304" />


#### Process Observations:

1. **`notepad.exe` (PID 4088):** Active instance of the target Windows text editor.
2. **`FTK Imager.exe` (PID 5992):** Forensic imaging tool loaded concurrently.
3. **Malware Signature Context:** Trailing string carve tracking within the memory environment revealed the footprint of a **Remcos RAT (Remote Access Trojan)** infection context manipulating text boundaries (`global const $ ( "vxwouoo{xnqt" , 2 )`).

#### Process Memory Carving & Credential Recovery

With the exact target process identity mapped (`notepad.exe` at PID `4088`), the virtual memory map space for that process was dumped directly to disk for string carving.

<img width="603" height="102" alt="image" src="https://github.com/user-attachments/assets/c234d978-e02f-443f-b69b-65688fff216b" />


Windows applications natively leverage 16-bit Little-Endian Unicode formatting to cache buffer allocations. A targeted string sweep was executed using broad regex boundaries to catch cleartext strings, passwords, or files matching the text editor profile context.

<img width="1207" height="752" alt="image" src="https://github.com/user-attachments/assets/123d6cf4-3ee1-4537-a710-6d49969fea1c" />


#### Recovered Memory Artifacts:

- **Active Buffer Document Name:** `SECRET_KEY.txt`
- **Exposed Credential Data:** `Bitlocker password: HackNyxAdmin`

#### Encrypted Volume Triage & Boundary Analysis

Attention was turned to the encrypted disk image `vault.dd`. Inspecting the file headers with the `file` command and a raw hex verification with `head` established the disk structural layout.

<img width="1520" height="257" alt="image" src="https://github.com/user-attachments/assets/1e2d899f-b551-4e2b-af60-f2d8ff1a5161" />


#### Observations:

- **Magic Signature Block:** The presence of the **`FVE-FS-`** marker explicitly identified the drive payload layout as an authentic **BitLocker Drive Encryption** container volume.
- **Partition Layout:** The drive image contained a structured Master Boot Record/GUID Partition Table layout rather than a raw standalone partition dump.

To isolate the exact sector offset where the primary encrypted data begins, `mmls` (SleuthKit) and `fdisk` were leveraged to map the disk boundaries.

<img width="627" height="222" alt="image" src="https://github.com/user-attachments/assets/442e895a-8cf7-4d90-81b4-a6913a95e812" />


**Partition Layout Mapping:**
• **Block 004:** Labeled as `Basic data partition`.
• **Sector Start Boundary:** Sector `128` (512 bytes per sector).
• **Calculated Byte Offset:** $128 \times 512 = 65536 \text{ bytes}$.
****

**Decryption & Disk Mounting**
To decrypt the drive cleanly without calculating offset bounds within user space, the Linux loopback subsystem was utilized to probe the image partitions automatically, followed by executing `dislocker` with the retrieved user password parameter (`-u`).

<img width="591" height="135" alt="image" src="https://github.com/user-attachments/assets/a34434e9-5e3d-4e73-bf85-d6c39fb5f9ab" />


Reviewing the newly unsealed `/media/vault` mounting node exposed a directory listing containing a spoofed file footprint asset:

<img width="587" height="165" alt="image" src="https://github.com/user-attachments/assets/0cef2049-c004-4557-b209-7a42bc0c8a55" />


#### Flag Restoration & Verification

The file payload was copied to the local staging folder and evaluated via hex verification (`xxd`).

<img width="552" height="127" alt="image" src="https://github.com/user-attachments/assets/975ec07e-38a1-445b-936b-7c656533f6b6" />


#### Analysis of Corrupted Headers:

The file extension was spoofed as a `.png`, but the internal signature string **`JFIF`** indicated that the file structure was a standard JPEG image. However, the first three magic header bytes were intentionally corrupted and overwritten with `67 67 67` (`ggg`).

A standard JPEG specification mandates that the initial stream bytes must correspond to the sequence **`FF D8 FF`**. A fast patch operation was automated using Python to fix the signature validation mask on disk.

<img width="561" height="256" alt="image" src="https://github.com/user-attachments/assets/3f26aab8-615f-483c-a7ee-2a80a594779c" />


Running `strings` on the repaired file structure to find if any tracking information was appended past the standard **`FF D9`** End of Image (EOI) JPEG sequence exposed a hidden string token trailing below the image footer space:

#### Final Decoding Step:

The trailing token featured classic `==` base64 padding architecture. Decoding the payload yielded the true target string structure.

<img width="571" height="190" alt="image" src="https://github.com/user-attachments/assets/4c2f0834-d91a-4ef0-b26f-87fe1e506c7b" />


```jsx
HNYX{d4S_cR4zy!}
```

we get the flag
