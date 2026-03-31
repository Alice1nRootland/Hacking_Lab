<img width="498" height="399" alt="image" src="https://github.com/user-attachments/assets/ca127032-6b10-463e-a981-cd8f74cae20d" />

We are given a small Flask application (`app.py`) and instructed to:

> analyse and find the vuln
> 
> 
> **flag: igoh25{md5(vuln)}**
> 

So our job is:

1. Read the source code
2. Identify the vulnerability
3. Determine the correct vulnerability keyword
4. MD5‑hash it
5. Submit inside the `igoh25{}` flag format

---

## **Given Source Code**

```python
#!/usr/bin/env python3
from flask import Flask, request, jsonify
import subprocess
import os
import re

app = Flask(__name__)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9._-]', '_', name)

@app.post("/process")
def process_file():
    data = request.get_json(silent=True)
    if not data or "filename" not in data:
        return jsonify({"error": "Missing filename"}), 400

    filename = sanitize_filename(data["filename"])
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.isfile(filepath):
        return jsonify({"error": "File not found"}), 404

    cmd = f"file {filepath}"
    try:
        output = subprocess.check_output(cmd, shell=True, text=True)
    except subprocess.CalledProcessError:
        return jsonify({"error": "Processing failed"}), 500

    return jsonify({"result": output})

@app.get("/")
def index():
    return jsonify({"message": "Upload files via SFTP, then POST /process"})

if __name__ == "__main__":
    app.run(host="0.0.0.0")

```

---

# **Vulnerability Analysis**

### ✔ Sanitization looks good…

The filename is passed through:

```python
sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9._-]', '_', name
```

This removes spaces, semicolons, pipes, quotes — which normally block command injection.

---

### But the real weakness:

```python
cmd = f"file {filepath}"
subprocess.check_output(cmd, shell=True)
```

`subprocess.check_output(..., shell=True)` is **extremely dangerous**.

Even if input looks filtered, `shell=True` executes the entire string through `/bin/sh`.

This makes the application vulnerable to **Command Execution (RCE)** when the filename can influence the shell in unexpected ways.

Examples:

- Using filenames that start with  to inject *command-line options*
- Using special files or symlinks
- Using shell globbing (, `?`) if sanitization is bypassed through upload tricks

In security classification, this falls under:

# **Vulnerability: RCE (Remote Code Execution)**

because user-controlled input reaches `shell=True`.

This is the simplest, most standard, CTF‑expected name.

---

#  **Flag Construction**

Challenge tells us:

```
flag = igoh25{md5(vuln)}
```

We identified:

```
vuln = rce
```

Compute MD5:

![image.png](attachment:885ca0c7-ab4c-4b98-84a7-70ac9ef1699b:image.png)

```bash
echo -n "rce" | md5sum
```

Output:

```
198717576b4bc32b47474c583ddc712a
```

---

# **Final Flag**

```
igoh25{198717576b4bc32b47474c583ddc712a}
```
