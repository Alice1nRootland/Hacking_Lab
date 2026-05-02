<img width="700" height="636" alt="image" src="https://github.com/user-attachments/assets/aea409a7-4814-4ae9-b17d-f238a5183eec" />

# Getting Closer — Full Write-Up & Explanation

## Overview

**Goal:** Analyze a malicious JS attachment that pulls a second-stage VBS, which in turn builds and runs an obfuscated PowerShell loader. The PS script downloads a JPG, carves an embedded Base64 payload, decodes it into a .NET binary, and executes it reflectively. The **flag** is inside that final payload.

**Flag (final):** `HTB{0n3_St3p_cl0s3r_t0_th3_cur3}`

---

## Artifacts & Environment

- **Given**: `vaccine.js` (from `Getting Closer.zip`)
- **Challenge infra**: expose services behind virtual hostnames
- **Hosts mapping** (cannot include ports):
    
    ```bash
    echo "94.237.57.1 infected.human.htb"   | sudo tee -a /etc/hosts
    echo "94.237.57.1 infected.zombie.htb"  | sudo tee -a /etc/hosts
    ```
    
    When curling, we include the **port `:52074`** and correct **Host** header.
    

## Stage 1 — JS Dropper (static triage)

**What it does (unobfuscated logic):**

- Creates `MSXML2.XMLHTTP.6.0`, `Scripting.FileSystemObject`, and `WScript.Shell`.
- Downloads **VBS** from: `http://infected.human.htb/d/BKtQR`
- Saves it under `C:\Windows\Temp\<random>.vbs`
- Executes it via `wscript "<temp>.vbs"`, then deletes it.

**Key indicators (IOCs):**

- `infected.human.htb`
- Path `/d/BKtQR`
- WSH components: `MSXML2.XMLHTTP.6.0`, `Scripting.FileSystemObject`, `WScript.Shell`

<img width="1294" height="403" alt="image" src="https://github.com/user-attachments/assets/54393eaf-a061-4d12-9c5b-6b09c4207b0b" />

## Stage 2 — VBS Second Stage (static/dynamic hints)

**What we see:**

- Heavy obfuscation; tons of random identifiers.
- Uses `Replace(...)` and `StrReverse(...)` for string assembly.
- Builds a large Base64 blob composed of chunks that look like `Jem9tYmllc...`.
- Contains many repeated `em9tYmllc` tokens — the write-up clue is that **`em9tYmllc` → "A"** before Base64 decoding (so it’s a disguised alphabet).

<img width="1353" height="724" alt="image" src="https://github.com/user-attachments/assets/ff6ffc29-fb85-4415-a8ff-00a094f32e37" />

- A **PowerShell** command that downloads an image from:
    
    ```
    http://infected.zombie.htb/WJveX71agmOQ6Gw_1698762642.jpg
    ```
    
- The script **carves** a Base64 section from the JPG (between specific offsets or markers), Base64-decodes it to a .NET assembly, then loads it via reflection.

> We didn’t need to fully emulate the VBS in this run—carving from the image is faster.
> 

## Stage 3 — PowerShell “stego” stage (carving from the image)

**Fetch the image safely:**

```bash
curl -sI -H "Host: infected.zombie.htb" \
  http://94.237.57.1:52074/WJveX71agmOQ6Gw_1698762642.jpg

curl -s  -H "Host: infected.zombie.htb" \
  http://94.237.57.1:52074/WJveX71agmOQ6Gw_1698762642.jpg -o /tmp/stego.jpg

file /tmp/stego.jpg
# -> JPEG image data
```

**Carve Base64-like data out of the JPG:**

```bash
# Extract long Base64 runs from the binary
grep -a -o -E '[A-Za-z0-9+/]{200,}={0,2}' /tmp/stego.jpg > /tmp/b64_runs.txt

awk '{print length, $0}' /tmp/b64_runs.txt | sort -nr | head -20
```

<img width="1289" height="655" alt="image" src="https://github.com/user-attachments/assets/b6386d1f-b183-4ac1-b5f0-ee7cdfc7c6e5" />

```php
tr -d '\n' < /tmp/b64_runs.txt > /tmp/payload.b64
base64 -d /tmp/payload.b64 > /tmp/payload.out 2>/tmp/b64.err || true

file /tmp/payload.out
# -> PE32+ executable for MS Windows ... Mono/.Net assembly
Find the flag in the .NET payload:

strings /tmp/payload.out | grep -E 'HTB\{|flag|key' -n | head
```

<img width="1286" height="299" alt="image" src="https://github.com/user-attachments/assets/d79e0183-29e7-4351-9210-dbd72bae59ad" />

thats our flag
