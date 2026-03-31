<img width="489" height="529" alt="image" src="https://github.com/user-attachments/assets/bb89f8cc-e8d1-47e2-8923-5dcf1ff8df53" />

**Challenge Name:** shazam_shell.ps1
**Category:** Reverse Engineering

### 1. Initial Analysis

We are presented with a file named `shazam_shell.ps1`. By running `cat shazam_shell.ps1` in the terminal, we can see the file content.

**Observation:**
The script consists of a single command that performs dynamic code execution. Let's break down the wrapper:

PowerShell

`& ([scriptblock]::Create([System.Text.Encoding]::Unicode.GetString([System.Convert]::FromBase64String('...BASE64_STRING...'))))`

- `[System.Convert]::FromBase64String(...)`: Takes the massive string and converts it from Base64 format into a byte array.
- `[System.Text.Encoding]::Unicode.GetString(...)`: Converts those bytes into a readable string using Unicode (UTF-16LE) encoding.
- `[scriptblock]::Create(...)` & `&`: This compiles the resulting string into code and executes it immediately.

### 2. The Strategy

To solve this, we do **not** want to execute the code (as it might be a reverse shell or malicious). Instead, we want to mimic the decoding steps to reveal the underlying code (the "payload") which likely contains the flag.

### 3. Solution

There are two main ways to solve this: using CyberChef or writing a quick Python decoder script.

### Method A: Using Python (Recommended for Kali)

Since you are already in a Kali environment, Python is the fastest way to decode this without leaving the terminal.

1. **Copy the Base64 String:** Copy the long string inside the single quotes `''` (starting with `DQAKACQA...`).
2. **Create a Solver Script:** Create a file named `solve.py`.

Python

`import base64

# Paste the long string from the ps1 file here
encoded_string = "DQAKACQAcgBQA..." 

# 1. Decode from Base64
decoded_bytes = base64.b64decode(encoded_string)

# 2. Decode bytes to String using UTF-16 (PowerShell 'Unicode' is usually UTF-16LE)
# We use 'utf-16' because the PS script specifically used [System.Text.Encoding]::Unicode
clear_text = decoded_bytes.decode('utf-16')

print(clear_text)`

1. **Run the Solver:**Bash
    
    `python3 solve.py`
    

### 2. The Result

Once decoded, the output usually reveals a second layer of PowerShell code. In CTF challenges like this, the flag is often hidden in a variable or printed out in the decoded text.

*Example of what the output might look like (Hypothetical):*

PowerShell

`$flag = "CTF{P0w3rSh3ll_D30bfusc4t10n_1s_Fun}"
Write-Host $flag
...`

### Summary of Flags/Key Indicators

- **Wrapper:** `[scriptblock]::Create`
- **Encoding:** Base64 -> UTF-16LE
- **Magic Bytes:** The Base64 starts with `DQAK`. In Base64/UTF-16LE, `DQA` usually decodes to a newline or a null byte sequence, which is common in PowerShell script headers.

```python

import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# --- Helper Function: Caesar Rotation ---
# Replicates the logic: [char](65+(($c-65+SHIFT)%26))
def rot_string(text, shift):
    result = []
    for char in text:
        if 'a' <= char <= 'z':
            # Rotate lowercase
            offset = ord('a')
            rotated = chr(offset + (ord(char) - offset + shift) % 26)
            result.append(rotated)
        elif 'A' <= char <= 'Z':
            # Rotate uppercase
            offset = ord('A')
            rotated = chr(offset + (ord(char) - offset + shift) % 26)
            result.append(rotated)
        else:
            # Keep numbers/symbols as is
            result.append(char)
    return "".join(result)

# --- Step 1: Extract Variables from the Obfuscated Script ---

# 1. The Encrypted Hex String (Needs ROT-2)
hex_source = "9488cyc19d5b9c63643dcyd801z2135b15zcbz6z3y6z5y660002c6633a70d1y2za8d9y6yyab536a72y3y0a45d85342y4361c07884zb1144257d71256cd38z419"
hex_clean = rot_string(hex_source, 2)
ciphertext_bytes = bytes.fromhex(hex_clean)

# 2. The AES Key Source (Needs ROT-6)
key_source = "6082700930681123" 
key_string = rot_string(key_source, 6)
key_bytes = key_string.encode('utf-8')

# 3. The AES IV Source (Needs ROT-24)
iv_source = "9592933780470478"
iv_string = rot_string(iv_source, 24)
iv_bytes = iv_string.encode('utf-8')

# --- Step 2: AES Decryption ---
# The script logic derives 'CBC' mode and 'PKCS7' padding.
try:
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
    decrypted_data = unpad(cipher.decrypt(ciphertext_bytes), AES.block_size)
    
    # This decrypted data becomes the XOR Key
    xor_key_string = decrypted_data.decode('utf-8')
    print(f"[+] AES Decryption Successful.")
    print(f"[+] XOR Key recovered: {xor_key_string}")

except Exception as e:
    print(f"[-] AES Decryption Failed: {e}")
    exit()

# --- Step 3: XOR Decryption ---

# 1. The XOR Payload Source (Needs ROT-1 then Base64 Decode)
xor_payload_source = "ZQLaFDDOUZ4uJZDcTB1kBPXCMxHpa14vzP1VBBnZPZ=="
xor_payload_clean = rot_string(xor_payload_source, 1)
xor_payload_bytes = base64.b64decode(xor_payload_clean)

# 2. Perform the XOR
flag_chars = []
for i in range(len(xor_payload_bytes)):
    # XOR byte with the key (looping the key if needed)
    key_char = xor_key_string[i % len(xor_key_string)]
    decrypted_byte = xor_payload_bytes[i] ^ ord(key_char)
    flag_chars.append(chr(decrypted_byte))

flag = "".join(flag_chars)

# --- Result ---
print("-" * 30)
print(f"FINAL FLAG: {flag}")
print("-" * 30)
```

After run the command, we will get this flag and need to convert into md5

<img width="603" height="141" alt="image" src="https://github.com/user-attachments/assets/cc0e8ce1-d6ba-40e4-a6bb-d5ddadafcd50" />

Flag : igoh25{f3bfb0a9a9e40152d7c0cbb5849d7421}
