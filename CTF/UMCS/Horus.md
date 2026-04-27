<img width="617" height="842" alt="image" src="https://github.com/user-attachments/assets/3ed9f79f-bd59-404a-b2c9-4ce715ba20b3" />

## Phase 1: Initial Triage

When we first get the file `horus.exe`, we need to know what we're looking at.

- **File Identification:** Using the `file` command in Kali reveals it is an **x64 PE32+ executable** for Windows.
- **Strings Analysis:** Running `strings` shows references to `IsDebuggerPresent`, `VirtualAlloc`, and a suspicious message: *"The application is updated. Please wait a moment."*
- **Architecture:** It’s a **Native x64 binary**, meaning we need a tool like **Binary Ninja** or **Ghidra** for the first layer.

<img width="840" height="73" alt="image" src="https://github.com/user-attachments/assets/ba1f8e50-235d-417f-824f-d34cdb993701" />

<img width="536" height="602" alt="image" src="https://github.com/user-attachments/assets/dd3e0ba1-fa72-4ba8-a853-a9dffc461132" />

### **Bypassing Protections**

Opening the file in **Binary Ninja**, the entry point led to a series of initialization routines. In `sub_140001440`, a call to `IsDebuggerPresent` was identified at `0x1400018f1`.

<img width="587" height="607" alt="image" src="https://github.com/user-attachments/assets/83f0e459-838e-4f69-83f1-d71a50c140e7" />

<img width="922" height="413" alt="image" src="https://github.com/user-attachments/assets/0707f818-b665-4ade-974b-b71c26df541a" />

<img width="830" height="602" alt="image" src="https://github.com/user-attachments/assets/d99d5723-d622-48e0-b42a-473f2a96a235" />

### **The Decryption Routine**

The core logic of `sub_140001440` involved:

1. **Memory Allocation:** Using `VirtualAlloc` to reserve `0x5bcc00` bytes.
2. **The Key:** A 64-bit constant was identified as the decryption key: **`0x4145013510415222`**.
3. **RC4 Algorithm:** The malware implements a standard RC4 stream cipher to decrypt the `.rdata` blob into the newly allocated memory.

### Technical Pivot: Static Decryption

Rather than relying on dynamic dumping (which was risky due to a 10-second self-deletion timer using `DeleteFileA`), a Python script was developed to decrypt the payload statically.

**Python Decryptor Snippet:**

Python

`import struct

# The constant key extracted from the native binary
key_val = -0x4145013510415222
key = struct.pack("<q", key_val)

# RC4 implementation for Stage 1
def decrypt_stage1(data, key):
    # ... KSA and PRGA logic ...
    return decrypted_bytes`

Running this script produced `decrypted_payload.exe`.

<img width="932" height="177" alt="image" src="https://github.com/user-attachments/assets/0ffd9882-0a55-4f9b-992d-2ae7ecb71324" />

### Stage 2: .NET Analysis (YouAreAnIdiot_UnFlash)

### **Decompilation**

The decrypted file was identified as a **.NET Assembly**. Using **dnSpy**, the source code was recovered. The namespace `YouAreAnIdiot_UnFlash` contained a class `CliLoader`.

<img width="1903" height="608" alt="image" src="https://github.com/user-attachments/assets/3097a11d-47f7-4c47-b981-d9311061606b" />

### **Final Flag Retrieval**

The .NET payload contained a secondary encryption layer:

- **Ciphertext:** A hardcoded hex string `cipherHex`.

<img width="1237" height="102" alt="image" src="https://github.com/user-attachments/assets/24e1f2d7-1fb8-4049-88f7-526567ea5dd3" />

- **Key Verification:** The program expected the same 64-bit key from Stage 1.
- **Custom Function:** A function named **`entahlahnak`** performed the final RC4 pass.

<img width="656" height="567" alt="image" src="https://github.com/user-attachments/assets/39f63bf5-a6a9-4bf8-b3bd-e39aeb470832" />

By applying the Stage 1 key to the `cipherHex` string, the flag was successfully decrypted.

<img width="881" height="493" alt="image" src="https://github.com/user-attachments/assets/5e2a91d8-8e1f-4d32-8638-4df496c0d0ec" />

