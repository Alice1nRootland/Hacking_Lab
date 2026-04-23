## Reconnaissance & Packer Identification

Just like the first challenge, the APK appeared to be a "Reforce" packed application. However, the internal logic had evolved.

**1. Initial Decompilation:**

<img width="717" height="309" alt="image" src="https://github.com/user-attachments/assets/2c547250-4de3-447e-8c4b-6fd18b9a2076" />

**2. Identifying the AES-GCM Logic:**
Inspecting `ProxyApplication.java` revealed a much more complex decryption routine compared to Challenge 1. Instead of a simple XOR loop, the app used **AES-GCM (Galois/Counter Mode)** with a key derived from a SHA-256 "fingerprint" of the `classes.dex` file.

## Phase 2: Defeating the AES-GCM Packer

The packer hid the real APK payload inside the `classes.dex` file, but with a twist: the payload length was stored in the last 4 bytes of the file.

**3. Extracting the packed DEX:**

<img width="551" height="97" alt="image" src="https://github.com/user-attachments/assets/9bef3abd-7969-4ada-891e-3cf8ade945b2" />

**4. Reconstructing the Key Derivation Function (KDF):**
We wrote a Python script to emulate the Java logic. The key steps were:
• **Zeroing out header fields:** To get a consistent SHA-256 hash, the app zeroed out the checksum, signature, and file size fields of the first 4096 bytes of the DEX.
• **Key/Nonce derivation:** * $Key = SHA256(Pepper + Fingerprint + 0x00)$
    ◦ $Nonce = SHA256(Pepper + Fingerprint + 0x01)[:12]$
• **Payload Extraction:** Reading the Big-Endian integer at the end of the file to determine the payload size.
**5. Executing the Decryptor:**
We ran our custom `crack_er2.py` script to derive the keys and unlock the inner APK.

```jsx
import hashlib
import struct
from Crypto.Cipher import AES

def solve():
    # 1. Load the packed classes.dex
    with open('classes.dex', 'rb') as f:
        dex_data = f.read()

    # 2. Extract payload using the Java logic (Last 4 bytes = Length)
    # Java's DataInputStream.readInt() is Big-Endian
    payload_len = struct.unpack('>I', dex_data[-4:])[0]
    payload = dex_data[-(4 + payload_len):-4]
    
    print(f"[*] Total file size: {len(dex_data)} bytes")
    print(f"[*] Detected Payload Length: {payload_len} bytes")

    # 3. Reconstruct the 'pepper' array from Java source
    # {109, -14, 71, -88, -32, -56, 58, -77, -34, 88, -123, 30, 23, -61, -87, 80, -42, -105, 38, 29, 18, 52, 86, 120, -102, -68, -34, -16, -85, -51, -17, 17}
    pepper = bytes([b % 256 for b in [
        109, -14, 71, -88, -32, -56, 58, -77, -34, 88, -123, 30, 
        23, -61, -87, 80, -42, -105, 38, 29, 18, 52, 86, 120, 
        -102, -68, -34, -16, -85, -51, -17, 17
    ]])

    # 4. Fingerprint the first 4096 bytes
    n = min(4096, len(dex_data))
    head = bytearray(dex_data[:n])
    # Zero out Checksum (8-12), Signature (12-32), and Size (32-36)
    for i in range(8, 12): head[i] = 0
    for i in range(12, 32): head[i] = 0
    for i in range(32, 36): head[i] = 0
    
    dex_digest = hashlib.sha256(head).digest()

    # 5. Derive AES Key and 12-byte Nonce
    # Key = SHA256(pepper + dex_digest + 0x00)
    # Nonce = First 12 bytes of SHA256(pepper + dex_digest + 0x01)
    key = hashlib.sha256(pepper + dex_digest + b'\x00').digest()
    nonce_full = hashlib.sha256(pepper + dex_digest + b'\x01').digest()
    nonce = nonce_full[:12]

    print(f"[*] Derived AES Key: {key.hex()}")
    print(f"[*] Derived Nonce: {nonce.hex()}")

    # 6. Decrypt using AES-GCM
    # The Java code returns cipher.doFinal(srcdata). 
    # In GCM, this means the authentication tag is at the END of the data.
    tag = payload[-16:]
    ciphertext = payload[:-16]
    
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    try:
        decrypted = cipher.decrypt_and_verify(ciphertext, tag)
        with open('unpacked_payload.zip', 'wb') as f:
            f.write(decrypted)
        print("[+] SUCCESS: Real app decrypted to unpacked_payload.zip")
    except Exception as e:
        print(f"[-] Decryption failed: {e}")
        # Final fallback: decrypt everything without tag
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        with open('unpacked_payload_raw.bin', 'wb') as f:
            f.write(cipher.decrypt(payload))
        print("[!] Saved raw buffer to unpacked_payload_raw.bin")

if __name__ == "__main__":
    solve()

```

<img width="718" height="175" alt="image" src="https://github.com/user-attachments/assets/d8ce0289-7aef-4e5d-b190-a81a8d10c6ef" />

## Phase 3: Analyzing the Inner Application

Once the payload was decrypted, we extracted the real application files.

**6. Unpacking the inner APK:**

<img width="750" height="361" alt="image" src="https://github.com/user-attachments/assets/d525a2bb-eeb4-41a4-a2e6-910f3fe8744a" />

**7. Static Analysis of the real code:**

We decompiled the new classes.dex and found that the MainActivity.java still used a native C++ function (encryptDataNative) to handle the background image.

<img width="601" height="109" alt="image" src="https://github.com/user-attachments/assets/e3da6af6-1666-4bd0-8361-a463859b4c82" />

**Phase 4: Bypassing the Login & Cryptanalysis**
The app featured a "Secure Login" screen with an MD5 check, but since we had access to the raw assets, we bypassed the UI entirely.
**8. Identifying the XOR Pattern:**
We compared the original decoy image (`background.txt`) with the encrypted asset (`background.bkp`). By XORing the first 100 bytes, we discovered a repeating pattern of **`0xEF`**.
**9. Decrypting the Flag Image:**
Instead of a 32-byte complex key like the first challenge, this stage used a single-byte XOR key ($0xEF$) for the asset itself.

<img width="1021" height="99" alt="image" src="https://github.com/user-attachments/assets/66e37418-8595-438e-b6da-70742d28303b" />

<img width="422" height="705" alt="image" src="https://github.com/user-attachments/assets/df32643d-16b4-4a6e-8a09-8a19fdcfcb8e" />

**`hack10{minato_namikaze}`**
