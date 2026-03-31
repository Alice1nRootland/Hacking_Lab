# **CTF Writeup — Reversing a PyInstaller Challenge (iGoH Edition)**

In this challenge, we were given a mysterious file named `chal`. Running the `file` command showed that it wasn’t a normal executable:

```bash
┌──(kali㉿kali)-[~/Desktop/igoh/re]
└─$ file chal
chal: data
```

So the file had no recognizable header — meaning the author likely **obfuscated** or **reversed** the bytes to hide the real content.

---

# Step 1 — Reverse the Entire File (Byte-by-Byte)

<img width="882" height="594" alt="image" src="https://github.com/user-attachments/assets/c9c43032-5433-44bb-a0ee-a088d9a67fc3" />

after i put some strings in ChatGPT it states the file code has been reversed

The aim was to reverse the whole binary **without altering the file type**.

Using text tools like `rev` or `tac` would corrupt binary data, so we use Perl to reverse bytes safely:

```bash
perl -0777 -pe '$_ = reverse $_' chal > chal_rev
```

The resulting file (`chal_rev`) remained `data`, but now in the **correct orientation** for extraction.

---

after i put some strings in chatgtpt it state the file code has been reversed

# Step 2 — Extract the PyInstaller Package

<img width="1293" height="481" alt="image" src="https://github.com/user-attachments/assets/7bbb9145-d3e9-4bd8-a985-790a2591d34e" />

After reversing, I tried to unzip it:

```bash
unzip chal_rev_extracted.zip
```

A full PyInstaller structure appeared:

- `libpython3.13.so`
- `base_library.zip`
- `_bz2.cpython-313-x86_64-linux-gnu.so`
- `PYZ-00.pyz_extracted`
- and finally, the juicy part:

```
main.pyc
```

This confirmed the challenge was a **PyInstaller-packed Python binary**, simply stored backwards.

---

# Step 3 — Decompile `main.pyc`

<img width="1279" height="687" alt="image" src="https://github.com/user-attachments/assets/7ceded2a-6824-47f0-ab25-142f68996650" />

Using **PyLingual**, I decompiled `main.pyc` into readable Python:

```python
from itertools import cycle
KEY = b'iGoH'
ENCODED_HEX = '00000000127e097b5c250c2e5b7e5f2b0c235f7a0d715a2b0b735b7858245a2d08720b7a5f3a'

def _hex_to_bytes(h: str) -> bytes:
    return bytes.fromhex(h)

def _xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes((b ^ k for b, k in zip(data, cycle(key))))

def main():
    encoded = _hex_to_bytes(ENCODED_HEX)
    flag_bytes = _xor_bytes(encoded, KEY)
    print('congratz you found me, but dig deeper')

```

The code clearly shows:

- The real flag is stored in `ENCODED_HEX`
- It is XOR‑encrypted with the repeating key `iGoH`
- The program prints a fake message to mislead solvers

Time to decode it manually.

---

# Step 4 — Write a Script to Recover the Flag

I wrote a simple solver:

```python
from itertools import cycle

KEY = b'iGoH'
ENCODED_HEX = '00000000127e097b5c250c2e5b7e5f2b0c235f7a0d715a2b0b735b7858245a2d08720b7a5f3a'

def xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes([b ^ k for b, k in zip(data, cycle(key))])

encoded = bytes.fromhex(ENCODED_HEX)
decoded = xor_bytes(encoded, KEY)

print("Decoded bytes:", decoded)
print("Decoded text :", decoded.decode())

```

Running it:

```bash
┌──(kali㉿kali)-[~/Desktop/igoh/re]
└─$ python3 solve.py

Decoded bytes: b'iGoH{9f35bcf290ced02d65cb4401c5ea5d26}'
Decoded text : iGoH{9f35bcf290ced02d65cb4401c5ea5d26}
```

---

# **Final Flag**

```
iGoH{9f35bcf290ced02d65cb4401c5ea5d26}
```
