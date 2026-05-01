<img width="700" height="641" alt="image" src="https://github.com/user-attachments/assets/2823c8cb-3240-4459-94f2-99784e1879a2" />

## **1. Initial Analysis**

- Received file: `UrgentPayment.doc`
- Checked with `strings`:

```bash
strings UrgentPayment.doc
```

**Observations:**

- Prompts: “Enable Editing”, “Enable Content” → **social engineering**
- Protected by Microsoft Office Protected View
- Embedded OLE streams, typical of Word documents with macros
- References to `Document_Open` and PowerShell

<img width="1856" height="736" alt="image" src="https://github.com/user-attachments/assets/c5d611e6-c61d-405a-99b8-9b769275da81" />

**2. Detect Macros with `olevba`**

`olevba UrgentPayment.doc` 

<img width="1861" height="743" alt="image" src="https://github.com/user-attachments/assets/0afc60a8-9821-472c-8953-f0447c81aed1" />

**Findings:**

- Auto-executing macro: `Document_Open`
- Reads environment variable: `Environ$("UserDomain")`
- Runs a **PowerShell encoded command** (`Shell("pOweRshElL -ec ...")`)
- **Suspicious keywords:** `Environ`, `Shell`, `vbNormalFocus`, `pOweRshElL`, **Hex Strings**

> These are classic indicators of malicious Office macros.
> 

## **Decode the PowerShell Command**

The PowerShell command is **base64 encoded in UTF-16LE**. To safely decode:

<img width="1865" height="159" alt="image" src="https://github.com/user-attachments/assets/bdb982a2-e9d8-4543-8ae7-8b786a936313" />

## **DE obfuscate PowerShell (Python)**

Malware used **character-by-character obfuscation**. Decoding safely with Python:

```python
template = "{5}{25}{8}{7}{0}{14}{3}{21}{2}{22}{15}{16}{31}{28}{11}{26}{17}{23}{27}{29}{10}{1}{6}{24}{30}{18}{13}{19}{12}{9}{20}{4}"
chars = [
    "B","U","4","B","%7D","ht","R_d","//ow.ly/HT","p:","T","0","_","N","M","%7","E","f","1T",
    "u","e","5","k","R","h","0","t","w","_","l","Y","C","U"
]

import re
indexes = [int(i) for i in re.findall(r"\{(\d+)\}", template)]
url = ''.join([chars[i] for i in indexes])
print("Decoded URL / Flag:", url)
```

<img width="1833" height="86" alt="image" src="https://github.com/user-attachments/assets/dc34fecf-6165-4e85-8e6f-c4c20fa8c3d7" />

## **. Decode URL-Encoded Flag**

- `%7B` → `{`
- `%7D` → `}`

**Final flag:**

```
HTB{k4REfUl_w1Th_Y0UR_d0CuMeNT5}
```

Flag successfully retrieved **without executing any malicious code**.
