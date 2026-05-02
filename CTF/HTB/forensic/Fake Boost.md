<img width="698" height="640" alt="image" src="https://github.com/user-attachments/assets/33f0d46c-8780-427b-af57-cbe9d3bfc02a" />

## Writeup — “Fake Boost” (how I recovered the flag, step-by-step)

Below is a compact lab-style writeup you can paste into a report. It includes the exact commands I ran, a short explanation for each step, and screenshot suggestions you can attach to your report.

---

### TL;DR — the flag

```
HTB{fr33_N17r0G3n_3xp053d!_b3W4r3_0f_T00_g00d_2_b3_7ru3_0ff3r5}
```

---

### Setup / files

I worked in `~/Desktop/htb`. The ZIP contained `capture.pcapng`. During analysis I exported HTTP objects to `http_objects/` (tools like `tshark`/`scapy`/`foremost`/Wireshark can do this) and used small scripts and `openssl`/`base64` to decode encrypted blobs.

## Inspect the capture and find interesting HTTP traffic

Commands and purpose:

```bash
# show pcap summary (optional)
capinfos capture.pcapng

# list top endpoints (to find suspicious host)
tshark -r capture.pcapng -q -z endpoints,ip

# find HTTP requests that refer to the "freediscordnitro" or suspicious path
tshark -r capture.pcapng -Y "http.request.uri contains freediscordnitro" -T fields -e tcp.stream
```

<img width="1363" height="798" alt="image" src="https://github.com/user-attachments/assets/0585119d-60c7-45b4-bfb9-e55d2a31ce90" />

<img width="1395" height="718" alt="image" src="https://github.com/user-attachments/assets/c19af536-65e8-43bd-bb9e-aadc94a8f79e" />

What I found:

- An HTTP GET for `/freediscordnitro` (stream 3).
- A POST to `/rj1893rj1joijdkajwda` (stream 48) with a long base64-ish body.

### Extract the Stage-2 script (downloaded by the GET)

Follow the TCP stream for the GET (tcp.stream = 3 in this case) to see the file the client downloaded:

```bash
# show the TCP stream content (ascii)
tshark -r capture.pcapng -q -z "follow,tcp,ascii,3" > stream3_follow.txt
# Inspect the save: it contained a PS1 payload filename (discordnitro.ps1)
sed -n '1,240p' stream3_follow.txt
```

<img width="1381" height="768" alt="image" src="https://github.com/user-attachments/assets/079e134a-bc83-4fd9-8568-0064cece2d38" />

<img width="1388" height="739" alt="image" src="https://github.com/user-attachments/assets/b0ecc156-b287-4349-8380-6896541b93f1" />

The GET returned a file named `discordnitro.ps1`. The script contained an obfuscated stage that later posts encrypted data to the server.

### Extract the POST body (the encrypted stage2 data)

Follow the TCP stream for the POST (tcp.stream = 48 here) and save the request body:

```bash
# follow TCP stream 48 and save to file
tshark -r capture.pcapng -q -z "follow,tcp,ascii,48" > stream48_follow.txt
# open it, find the long base64 blob (the POST body)
sed -n '1,240p' stream48_follow.txt
```

Inside `stream48_follow.txt` we see a long base64-like blob at the POST body.

<img width="1390" height="663" alt="image" src="https://github.com/user-attachments/assets/2b51a1f5-071e-4df5-b369-1cebbd32335b" />

### Identify AES key and cipher parameters (from the PS1)

In the stage-2 PS1 (downloaded earlier as `discordnitro.ps1` or embedded), there was a base64 AES key:

```
$AES_KEY = "Y1dwaHJOVGs5d2dXWjkzdDE5amF5cW5sYUR1SWVGS2k="
```

This decodes to a 32-byte AES key:

```bash
echo "Y1dwaHJOVGs5d2dXWjkzdDE5amF5cW5sYUR1SWVGS2k=" | base64 -d > key.raw
xxd -p -c 256 key.raw
# hex key looks like: 63577068724e546b397767575a39337431396a6179716e6c6144754965464b69
```

Explanation: The PS1 `Encrypt-String` prepends the AES IV to the ciphertext and then base64-encodes the result. So we expect `ct = IV || ciphertext` in base64 form.

### Decode POST body and decrypt AES -> recover JSON (second half of flag inside)

I extracted the base64 payload from `stream48_follow.txt`, decoded it to binary `ct.bin`, split IV and ciphertext, and used OpenSSL to decrypt (AES-256-CBC). Commands:

```bash
# extract the base64 blob (first long match)
grep -Eho '[A-Za-z0-9+/]{40,}={0,2}' stream48_follow.txt | head -n1 > b64.txt

# decode to raw bytes
base64 -d b64.txt > ct.bin

# extract IV (first 16 bytes) and ciphertext
xxd -p -l 16 ct.bin > iv.hex
IVHEX=$(cat iv.hex | tr -d '\n')
dd if=ct.bin of=cipher_after_iv.bin bs=1 skip=16 status=none

# get key hex
KEYHEX=$(xxd -p -c 256 key.raw)

# decrypt (AES-256-CBC, the IV was prefixed)
openssl enc -aes-256-cbc -d -in cipher_after_iv.bin -K "$KEYHEX" -iv "$IVHEX" -nosalt -out try_ivpref.txt 2>/dev/null || true

# show the decrypted output
sed -n '1,200p' try_ivpref.txt
```

<img width="1394" height="630" alt="image" src="https://github.com/user-attachments/assets/84daf643-dd68-43ca-aae9-d526a1954799" />

Result:

- `try_ivpref.txt` contained JSON with Discord user info. One field (Email) was base64-encoded string:
    
    `YjNXNHIzXzBmX1QwMF9nMDBkXzJfYjNfN3J1M18wZmYzcjV9`
    

Decode that base64:

```bash
echo "YjNXNHIzXzBmX1QwMF9nMDBkXzJfYjNfN3J1M18wZmYzcjV9" | base64 -d
# yields:
b3W4r3_0f_T00_g00d_2_b3_7ru3_0ff3r5}
```

<img width="1397" height="83" alt="image" src="https://github.com/user-attachments/assets/bb65d15c-bd92-418f-8741-90ca68820636" />

This is the **second half** of the flag:

```
b3W4r3_0f_T00_g00d_2_b3_7ru3_0ff3r5}
```

### Recover the first half (embedded inside the Stage-1 payload)

The `discordnitro.ps1` contained a big reversed base64 payload string (`$jozeq3n`). I extracted and reversed it, then base64-decoded to obtain `stage1_payload.ps1`. Commands used:

```bash
# extract the quoted blob assigned to $jozeq3n and save to bigblob.txt
python3 - <<'PY'
import re, pathlib, sys
s = pathlib.Path("http_objects/freediscordnitro").read_text(errors="ignore")
m = re.search(r'\$jozeq3n\s*=\s*"([^"]+)"\s*;', s, re.S)
if not m:
    print("[-] $jozeq3n not found")
    sys.exit(1)
open("bigblob.txt","w").write(m.group(1))
print("[+] extracted length:", len(m.group(1)))
PY

# reverse and decode (the PS1 reversed before base64-decoding)
rev bigblob.txt > bigblob_rev.txt
tr -d '\r\n' < bigblob_rev.txt > bigblob_rev_clean.txt
base64 -d bigblob_rev_clean.txt > stage1_payload.ps1

# inspect the payload
sed -n '1,240p' stage1_payload.ps1
```

<img width="1391" height="787" alt="image" src="https://github.com/user-attachments/assets/c0b74040-789c-4577-96c4-2a17fb4a81e1" />

<img width="1387" height="803" alt="image" src="https://github.com/user-attachments/assets/b0e17894-48d3-4144-812b-60de9aa457f3" />

Inside `stage1_payload.ps1` I found a variable `$part1`:

```powershell
$part1 = "SFRCe2ZyMzNfTjE3cjBHM25fM3hwMDUzZCFf"
```

Decode that base64:

```bash
echo "SFRCe2ZyMzNfTjE3cjBHM25fM3hwMDUzZCFf" | base64 -d
# yields:
HTB{fr33_N17r0G3n_3xp053d!_
```

<img width="1383" height="92" alt="image" src="https://github.com/user-attachments/assets/6c587eed-6487-4333-85b0-8a47bfc35da7" />

This is the **first half** of the flag:

```
HTB{fr33_N17r0G3n_3xp053d!_
```

That is the final flag (repeat):

```
HTB{fr33_N17r0G3n_3xp053d!_b3W4r3_0f_T00_g00d_2_b3_7ru3_0ff3r5}
```

---

# Notes, explanations & sanity checks

- Why reversing? — The PS1 used `.ToCharArray()` and `[array]::Reverse(...)` before `FromBase64String(...)`. That is the reason the embedded blob was reversed before base64-decoding.
- Why IV prefix? — The `Encrypt-String` function in the PS1 prepends `AesManaged.IV` to the ciphertext and then base64 encodes. So the TLS POST body base64 decoded into `IV||ciphertext`.
- Why AES key is base64? — The PS1 stored the AES key as base64 (`$AES_KEY = "..."`), so we had to base64-decode it to use with OpenSSL.
- File cleanup — Keep artifacts (ct.bin, try_ivpref.txt, stage1_payload.ps1) as evidence.
