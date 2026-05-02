<img width="1766" height="775" alt="image" src="https://github.com/user-attachments/assets/a0b93cf8-a84b-43b9-a873-0ad2b62b02d4" /><img width="702" height="647" alt="image" src="https://github.com/user-attachments/assets/47b06c2f-b8de-4f62-945a-8a08f6ea0549" />

# Writeup Automation

Below is a concise, reproducible step‑by‑step forensic writeup showing how I analyzed the provided `capture.pcap` and recovered the two parts of the HTB flag. It includes the commands I ran, why I ran them, what I looked for, and suggested screenshots to include in a final report. You can copy/paste any of the commands into your investigation VM.

---

## Summary (one‑line)

The PCAP contained a DNS‑based PowerShell C2 using `windowsliveupdater.com`. We extracted an AES‑encrypted PowerShell stager from an HTTP response, decoded the hardcoded AES key from the stager, used it to decrypt DNS TXT records (which contained commands), and reconstructed exfiltrated output built from DNS A subdomain labels to reveal the second flag part. Final assembled flag:

```
HTB{y0u_c4n_4utom4t3_but_y0u_c4nt_h1de}
```

## Quick triage / protocol overview

**Goal:** see which protocols and endpoints dominate traffic.

**Commands:**

```bash
tshark -r capture.pcap -q -z conv,ip
tshark -r capture.pcap -q -z io,phs
```

**Why:** This reveals heavy talkers and which protocols to focus on (DNS, HTTP, TLS, etc.). In this case DNS + some HTTP stood out.

<img width="1766" height="775" alt="image" src="https://github.com/user-attachments/assets/686ed19e-fa03-4c9a-98d9-28520c842c63" />

## Look for suspicious DNS patterns

**Goal:** find unusual domains / beacon patterns.

**Commands:**

```bash
tshark -r capture.pcap -Y "dns.qry.name" -T fields -e dns.qry.name | sort | uniq -c | sort -nr | head -n 50
```

**What to look for:** repeated queries for similar domain(s), very long/hex-like subdomains, `start.`/`end.` markers.

<img width="1850" height="832" alt="image" src="https://github.com/user-attachments/assets/e832f5be-2001-4d60-8d45-52a26adbf1e8" />

**Result observed:** many queries for `*.windowsliveupdater.com`, including `start.windowsliveupdater.com` and numerous 32‑hex labels like `99B8CE3D...windowsliveupdater.com`.

## Map DNS names to IPs (confirm C2 server)

**Goal:** see which A answers point to what IPs.

**Command:**

```bash
tshark -r capture.pcap -Y "dns.qry.name contains windowsliveupdater.com && dns && dns.a" -T fields -e frame.time -e dns.qry.name -e dns.a | sort -u
```

<img width="1710" height="772" alt="image" src="https://github.com/user-attachments/assets/04a40eea-0b75-49a8-86eb-e533d7bf2bd9" />

**Result observed:** TXT/A responses pointed to `147.182.172.189` (C2) and HTTP connected to `77.74.198.52:80`.

**Why it matters:** confirms infrastructure and where payloads/responses were coming from.

## Inspect HTTP traffic to C2 (extract potential payload)

**Goal:** find the HTTP request/response that delivered the stager.

**Commands:**

```bash
tshark -r capture.pcap -Y http.request -T fields -e frame.number -e frame.time -e ip.src -e http.host -e http.request.uri -e http.user_agent
# find the frame number of the suspect GET (e.g. /desktop.png)
```

From earlier analysis we found:

```
frame 1926 : GET /desktop.png  Host: windowsliveupdater.com  Node: 77.74.198.52
```

<img width="1771" height="598" alt="image" src="https://github.com/user-attachments/assets/8969070e-f225-413f-8531-76c210983784" />

**Extract the TCP stream:**

```bash
tshark -r capture.pcap -q -z follow,tcp,raw,17 > stream_17.raw
# (obtain stream number with: tshark -r capture.pcap -Y "frame.number==1926" -T fields -e tcp.stream)
```

**Inspect raw stream:**

```bash
file stream_17.raw
xxd -l 256 stream_17.raw | sed -n '1,40p'
strings stream_17.raw | head
```

<img width="1771" height="813" alt="image" src="https://github.com/user-attachments/assets/44db6c1e-c1b6-425b-b482-a587a4790208" />

**What we found:** the HTTP response body in that stream was hex‑encoded ASCII (headers in hex then base64 payload). The response included base64 text beginning with `ZnVuY3Rp...` (Base64 of a PowerShell script).

## Convert hex → binary, extract base64, decode to readable PowerShell

**Commands:**

```bash
# extract long hex runs from stream
grep -oE '[0-9A-Fa-f]{200,}' stream_17.raw > hex_blob.txt

# convert hex ASCII to binary
xxd -r -p hex_blob.txt > hex_blob.bin

# extract base64-like runs from the binary
strings hex_blob.bin | egrep -o '[A-Za-z0-9+/=]{100,}' > payload_extracted.b64

# decode base64 (yields a plaintext PowerShell script)
base64 -d payload_extracted.b64 > payload_raw.bin
file payload_raw.bin
xxd -l 128 payload_raw.bin | sed -n '1,40p'
```

<img width="1758" height="531" alt="image" src="https://github.com/user-attachments/assets/38dda04c-d975-4464-9009-91777baa0415" />

<img width="1759" height="775" alt="image" src="https://github.com/user-attachments/assets/47bd59f7-3282-44ba-a865-b13788a1b09e" />

**What we found:** `payload_raw.bin` contained the AES helper PowerShell functions and code — specifically `Create-AesManagedObject`, `Encrypt-String`, `Decrypt-String` and the hardcoded key:

```
$key = "a1E4MUtycWswTmtrMHdqdg=="
```

It also included logic that:

- performs a `Resolve-DnsName -type TXT ...` against `windowsliveupdater.com` on server `147.182.172.189`,
- decrypts TXT strings, `iex` them,
- encrypts command output, `parts 32`, and exfiltrates each chunk by resolving `.windowsliveupdater.com` A records with `start`/`end` markers.

## Decode the AES key (for human readability)

**Command:**

```bash
echo "a1E4MUtycWswTmtrMHdqdg==" | base64 -d
# result: binary key; treat as bytes — we used it directly in decrypt scripts
```

**Note:** The key is base64 for convenience in script. We'll feed it into our decryptor.

## Extract DNS TXT records (these are the encrypted commands)

**Command:**

```bash
tshark -r capture.pcap -Y 'dns.qry.type==16 && dns.qry.name contains "windowsliveupdater.com"' -T fields -e dns.txt > dns_txt_lines.raw
# split commas so each base64 string is on its own line
cat dns_txt_lines.raw | tr ',' '\n' | sed 's/^[[:space:]]*//; s/[[:space:]]*$//' > encrypted_chunks_full.txt
wc -l encrypted_chunks_full.txt
sed -n '1,120p' encrypted_chunks_full.txt
```

<img width="1767" height="423" alt="image" src="https://github.com/user-attachments/assets/453a92d3-10bd-48a8-abac-19668c3720fe" />

**Result:** a list of base64 strings (each is IV|ciphertext base64) — these decrypt to commands (e.g., `hostname`, `whoami`, `ipconfig`, etc.).

## Decrypt the DNS TXT records (Python)

**Script:** `decrypt_payload.py` (uses `pycryptodome`)

```python
# decrypt_payload.py (short summary)
# - key_b64 = "a1E4MUtycWswTmtrMHdqdg=="
# - for each base64 record: base64.b64decode -> iv = first 16 bytes -> AES-CBC decrypt with key -> strip trailing nulls -> decode to utf-8
#!/usr/bin/env python3
# decrypt_payload.py
# Usage: python3 decrypt_payload.py encrypted_chunks.txt

import sys
import base64
from Crypto.Cipher import AES

def decrypt_aes_cbc_with_iv(key_b64, b64_payload):
    """
    key_b64: base64-encoded AES key (string)
    b64_payload: base64-encoded (IV + ciphertext)
    returns: decrypted utf-8 string (nulls stripped)
    """
    try:
        key = base64.b64decode(key_b64)
    except Exception as e:
        raise ValueError("Bad base64 key: %s" % e)

    try:
        data = base64.b64decode(b64_payload)
    except Exception as e:
        raise ValueError("Bad base64 payload: %s" % e)

    if len(data) < 17:
        raise ValueError("Decoded payload too short to contain IV + ciphertext")

    iv = data[:16]
    ct = data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = cipher.decrypt(ct)
    # PowerShell used zero padding; strip trailing null bytes
    pt = pt.rstrip(b'\x00')
    try:
        return pt.decode('utf-8', errors='ignore')
    except Exception:
        return pt.decode('latin1', errors='ignore')

def load_records(fname):
    s = open(fname, "rb").read().decode('utf-8', errors='ignore').strip()
    # split on commas and newlines (records may be comma-separated)
    parts = []
    for chunk in s.replace("\r", "\n").split("\n"):
        if not chunk:
            continue
        # chunk may contain comma-separated items
        for item in chunk.split(","):
            item = item.strip()
            if item:
                parts.append(item)
    return parts

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 decrypt_payload.py encrypted_chunks.txt")
        sys.exit(1)

    infile = sys.argv[1]
    try:
        records = load_records(infile)
    except Exception as e:
        print("Failed to read input file:", e)
        sys.exit(2)

    if not records:
        print("No records found in", infile)
        sys.exit(3)

    # Key from payload (base64)
    key_b64 = "a1E4MUtycWswTmtrMHdqdg=="

    print("[*] Loaded %d encrypted records from %s\n" % (len(records), infile))
    for i, rec in enumerate(records, start=1):
        print("=== Record %d ===" % i)
        print("[Encrypted]:", rec)
        try:
            dec = decrypt_aes_cbc_with_iv(key_b64, rec)
            print("[Decrypted]:")
            # print safely, but not executing anything
            print(dec)
        except Exception as e:
            print("[!] Decrypt failed:", e)
        print()

if __name__ == "__main__":
    main()
```

**Run:**

```bash
pip3 install pycryptodome
python3 decrypt_payload.py encrypted_chunks_full.txt | sed -n '1,200p'
```

<img width="1363" height="701" alt="image" src="https://github.com/user-attachments/assets/b9c0a147-9ffc-41bc-8bec-0fe5d7f746ca" />

**Interpretation:** the operator remotely instructed the victim to create a privileged user with password `JHBhcnQxPSdIVEJ7eTB1X2M0bl8n` (this is base64), enabled RDP in firewall and started the TermService — clear lateral movement/persistence staging.

## Decode first part of flag from the created user password

**Command:**

```bash
echo "JHBhcnQxPSdIVEJ7eTB1X2M0bl8n" | base64 -d
# Output: $part1='HTB{y0u_c4n_
```

**Interpretation:** the attacker’s command inserted a string that contains `$part1='HTB{y0u_c4n_` — that is the **first part of the flag**. In the CTF we recorded that as the first flag half

## Reconstruct exfiltrated output (the second part) from DNS A queries

**Goal:** the implant encrypted command output and sent it back in chunks via A‑record queries like `<HEX32>.windowsliveupdater.com`. We must capture those qnames in order between `start.` and `end.` markers, join the 32‑byte hex labels, convert hex→bytes, then decrypt the combined IV|ciphertext.

**Commands to gather qnames (chronological):**

```bash
tshark -r capture.pcap -Y 'dns.qry.name contains "windowsliveupdater.com"' -T fields -e frame.time_epoch -e dns.qry.name | sort -n > qnames.txt
sed -n '1,120p' qnames.txt
```

<img width="1757" height="804" alt="image" src="https://github.com/user-attachments/assets/41651d9c-03d4-4e73-b2ac-630f49f8c4fe" />

**Script:** `reconstruct_exfil.py` — it:

- groups labels between `start.` and `end.`,
- concatenates the hex labels,
- converts to bytes,
- decrypts with AES key (`a1E4MUtycWswTmtrMHdqdg==`).

```php
#!/usr/bin/env python3
# reconstruct_exfil.py
# Usage: python3 reconstruct_exfil.py qnames.txt

import sys, re, base64
from Crypto.Cipher import AES

if len(sys.argv) < 2:
    print("Usage: python3 reconstruct_exfil.py qnames.txt")
    sys.exit(1)

fname = sys.argv[1]
lines = [l.strip() for l in open(fname,'r',encoding='utf-8',errors='ignore').read().splitlines() if l.strip()]

# regex to capture qname
hex_label_re = re.compile(r'^([0-9A-Fa-f]{32})\.windowsliveupdater\.com$')
start_re = re.compile(r'^start\.windowsliveupdater\.com$')
end_re = re.compile(r'^end\.windowsliveupdater\.com$')

segments = []   # list of lists of hex chunks
current = None

for ln in lines:
    # line format: "<epoch> <qname>"
    parts = ln.split(None, 1)
    if len(parts) == 1:
        q = parts[0]
    else:
        q = parts[1].strip()
    # check start
    if start_re.match(q):
        current = []
        continue
    if end_re.match(q):
        if current is not None:
            segments.append(current)
            current = None
        continue
    m = hex_label_re.match(q)
    if m and current is not None:
        current.append(m.group(1))

# If no segments found, try a fallback: take any hex labels in order
if not segments:
    fallback = []
    for ln in lines:
        parts = ln.split(None,1)
        q = parts[1].strip() if len(parts)>1 else parts[0].strip()
        m = hex_label_re.match(q)
        if m:
            fallback.append(m.group(1))
    if fallback:
        segments.append(fallback)

if not segments:
    print("No hex segments found. Check qnames.txt content.")
    sys.exit(2)

# AES key (base64 from payload)
key_b64 = "a1E4MUtycWswTmtrMHdqdg=="
key = base64.b64decode(key_b64)

def decrypt_hex_hexcombo(hexstring):
    # hexstring is concatenated hex (IV + ciphertext) in hex chars
    data = bytes.fromhex(hexstring)
    if len(data) < 17:
        return None, "data too short"
    iv = data[:16]
    ct = data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = cipher.decrypt(ct)
    # PowerShell used zero padding; strip trailing nulls
    pt = pt.rstrip(b'\x00')
    try:
        return pt.decode('utf-8', errors='replace'), None
    except Exception as e:
        return pt, str(e)

# Process each segment
for idx, seg in enumerate(segments, start=1):
    print("=== Segment %d: %d chunks ===" % (idx, len(seg)))
    hex_concat = "".join(seg)
    # decrypt
    plaintext, err = decrypt_hex_hexcombo(hex_concat)
    if err:
        print("[!] Decrypt error:", err)
        # dump initial bytes as hex for debugging
        print("Hex len:", len(hex_concat), "chars,", len(hex_concat)//2, "bytes")
    else:
        print("[Decrypted plaintext follows]\n")
        print(plaintext)
    print("\n---------------------------\n")
```

**Run:**

```bash
python3 reconstruct_exfil.py qnames.txt | sed -n '1,240p'
```

<img width="1773" height="794" alt="image" src="https://github.com/user-attachments/assets/f765af60-d45d-420a-8a14-569341389e46" />

**Result:** several decrypted segments. The reconstructed plaintext contained lots of binary/noise (typical of console output), but also human-readable fragments. One segment included:

```
... $part2=4utom4t3_but_y0u_c4nt_h1de}
```

**Interpretation:** the second part of the flag was reconstructed — after minor leet/character restoration we get the string `4utom4t3_but_y0u_c4nt_h1de}`.

## Assemble final flag

We combine the earlier `$part1` and the `$part2` to form the final HTB flag:

```
$part1  = HTB{y0u_c4n_
$part2  = 4utom4t3_but_y0u_c4nt_h1de}
```

Submit:

```
HTB{y0u_c4n_4utom4t3_but_y0u_c4nt_h1de}
```

thats our flag!
