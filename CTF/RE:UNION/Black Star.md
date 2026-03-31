<img width="499" height="513" alt="image" src="https://github.com/user-attachments/assets/9ed09e3a-a192-4902-93a1-216cce0c11db" />

# CTF Writeup: RC6 Reverse Engineering Challenge

## 1. Challenge Overview

**Category:** Reverse Engineering
**Objective:** The binary takes a user input (flag), encrypts it, and compares it against a hardcoded, obfuscated buffer in memory. We need to reverse the encryption logic and the obfuscation layers to recover the flag.

## 2. Static Analysis

### The Main Logic (`sub_8049120`)

<img width="1547" height="566" alt="image" src="https://github.com/user-attachments/assets/09a5bd6d-47dd-429b-9b80-86e92bef9289" />

We start by analyzing the main function. The logic flows as follows:

1. **Banner & Setup:** It prints a banner and a story about a "collapsing star."
2. **Global Data Modification:** It calls `sub_80497F0()`. This is crucial. It modifies the global array `xmmword_804C060` (where the encrypted flag is stored) *before* the user input is even processed.
3. **Key Setup:** It calls `sub_8049600` with the key string:
`"0123456789abcdef0123456789abcdef"`
4. **Input Loop:**
    - It reads the user's input (the flag).
    - It pads the input to a multiple of 16 bytes.
    - It processes the input 16 bytes at a time.

### Identifying the Cipher (RC6)

Inside the key setup (`sub_8049600`) and encryption (`sub_8049700`) functions, we see distinct signatures:

- **Magic Constants:** The code uses `1209970333` (`0xB7E15163`) and `1640531527` (which relates to `0x9E3779B9`). These are the **Golden Ratio constants (P32 and Q32)** used specifically in the **RC5** and **RC6** encryption algorithms.
- **The "Quadratic Rotation":** Inside the encryption loop `sub_8049700`, we see this line:C
    
    `v6 = __ROL4__(v3 * (2 * v3 + 1), 5);`
    
    This operation, f(x)=x(2x+1), is the hallmark of **RC6**.
    

**Cipher Params:**

- **Block Size:** 128-bit (16 bytes)
- **Key Size:** 256-bit (32 bytes)
- **Rounds:** 20 (The loop runs 20 times)

### The Obfuscation Layers

The author added two layers of obfuscation to prevent standard tools from just decrypting it.

**Layer 1: Input Transformation (The SIMD Twist)**
Before the RC6 encryption happens, the input block (`v6`) is transformed:

C

`v10 = _mm_or_si128(_mm_slli_epi64(v6, 0x11u), _mm_srli_epi64(v6, 0x2Fu));`

- `0x11` (17) + `0x2F` (47) = 64.
- This is a **Rotate Left by 17 bits** applied to each 64-bit half of the 128-bit block.
- *Solution:* We must **Rotate Right by 17 bits** after decrypting.

**Layer 2: Target Data Obfuscation**
The function `sub_80497F0` runs at the start of the program:

C

- `((_BYTE *)xmmword_804C060 + v6) = __ROR1__(*((_BYTE *)xmmword_804C060 + v6), 3);`

It iterates through the encrypted flag stored in the binary and rotates every single byte **Right by 3**.

- *Solution:* To reconstruct the valid ciphertext for comparison, we must take the raw bytes from the file and apply **ROR(3)** to them.

---

## 3. Data Extraction

We needed the raw encrypted bytes from the binary. Using `xxd` on the binary provided the raw hex dump.

**Command:**

Bash

`xxd -g 1 chall | grep -i -A 3 "3f 70 bd c8"`

<img width="1410" height="124" alt="image" src="https://github.com/user-attachments/assets/45460ba9-8fff-4ec5-9553-27d0b8debadf" />

**Extracted Data (48 bytes):**

1. `3f 70 bd c8 ed b2 96 20 21 1b 1a c1 70 7f c5 cb`
2. `5a 92 dd 56 f0 ea f6 12 3a ce 0f 5c a3 b3 7c 87`
3. `db 49 80 0b bc e8 65 3e 1f 22 10 89 87 56 1e 22`

---

## 4. Solution Script

This script implements the RC6 decryption, handles the key expansion, applies the obfuscation fixes, and prints the flag.

Python

```php
import struct

# --- 1. The Encrypted Data (Extracted from binary) ---
FULL_HEX_DUMP = (
    "3f70bdc8edb29620211b1ac1707fc5cb"
    "5a92dd56f0eaf6123ace0f5ca3b37c87"
    "db49800bbce8653e1f22108987561e22"
)

# --- 2. The Key (Hardcoded in binary) ---
KEY_STR = b"0123456789abcdef0123456789abcdef"

# --- Helper Functions ---
def ROL(x, n, bits=32):
    return ((x << n) | (x >> (bits - n))) & ((1 << bits) - 1)

def ROR(x, n, bits=32):
    return ((x >> n) | (x << (bits - n))) & ((1 << bits) - 1)

def ROR64(x, n):
    return ((x >> n) | (x << (64 - n))) & 0xFFFFFFFFFFFFFFFF

# --- RC6 Key Schedule ---
def generate_round_keys(key_data):
    P32 = 0xB7E15163
    Q32 = 0x9E3779B9
    ROUNDS = 20
    
    c = len(key_data) // 4
    L = list(struct.unpack(f'<{c}I', key_data))
    S = [(P32 + i * Q32) & 0xFFFFFFFF for i in range(2 * ROUNDS + 4)]
    
    A = B = i = j = 0
    v = 3 * max(c, 2 * ROUNDS + 4)
    
    for _ in range(v):
        A = S[i] = ROL((S[i] + A + B) & 0xFFFFFFFF, 3, 32)
        B = L[j] = ROL((L[j] + A + B) & 0xFFFFFFFF, (A + B) % 32, 32)
        i = (i + 1) % len(S)
        j = (j + 1) % len(L)
    return S

# --- RC6 Decrypt Core ---
def rc6_decrypt_block(block_bytes, S):
    ROUNDS = 20
    A, B, C, D = struct.unpack('<4I', block_bytes)
    
    # Undo Post-whitening
    C = (C - S[2 * ROUNDS + 3]) & 0xFFFFFFFF
    A = (A - S[2 * ROUNDS + 2]) & 0xFFFFFFFF
    
    # Unroll Rounds
    for i in range(ROUNDS, 0, -1):
        (A, B, C, D) = (D, A, B, C)
        u = ROL((D * (2 * D + 1)) & 0xFFFFFFFF, 5, 32)
        t = ROL((B * (2 * B + 1)) & 0xFFFFFFFF, 5, 32)
        C = (ROR((C - S[2 * i + 1]) & 0xFFFFFFFF, t % 32, 32) ^ u)
        A = (ROR((A - S[2 * i]) & 0xFFFFFFFF, u % 32, 32) ^ t)

    # Undo Pre-whitening
    D = (D - S[1]) & 0xFFFFFFFF
    B = (B - S[0]) & 0xFFFFFFFF
    
    return struct.pack('<4I', A, B, C, D)

# --- Main Solver Logic ---
def solve():
    print(f"[*] Parsing {len(FULL_HEX_DUMP)//2} bytes of encrypted data...")
    raw_data = bytes.fromhex(FULL_HEX_DUMP)
    S = generate_round_keys(KEY_STR)
    
    flag = b""

    for i in range(0, len(raw_data), 16):
        block = raw_data[i : i+16]
        
        # Step 1: Replicate the Global Data Obfuscation (ROR 3)
        # The binary does ROR(3) on the data in memory. We must do the same
        # to match the state of the data when it was compared.
        target_cipher = bytearray([ROR(b, 3, 8) for b in block])
        
        # Step 2: Decrypt using RC6
        decrypted_block = rc6_decrypt_block(target_cipher, S)
        
        # Step 3: Reverse the SIMD Input Transformation
        # The binary did: Rotate Left 17 on 64-bit chunks.
        # We must do: Rotate Right 17.
        v1, v2 = struct.unpack('<QQ', decrypted_block)
        v1 = ROR64(v1, 17)
        v2 = ROR64(v2, 17)
        
        flag += struct.pack('<QQ', v1, v2)

    print(f"\n[+] Flag Found: {flag.decode('utf-8').strip()}")

if __name__ == "__main__":
    solve()
```

<img width="1425" height="833" alt="image" src="https://github.com/user-attachments/assets/02a3f62b-fb4e-4b44-aa19-83ab7e114924" />

## 5. The Flag

Running the script produces:

Plaintext

`[*] Parsing 48 bytes of encrypted data...

[+] Flag Found: RE:CTF{b14CKS74R_c0LL4ps3s_1n70_7h3_v01D_0f_RC6}`
