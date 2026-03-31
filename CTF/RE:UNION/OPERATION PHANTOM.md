<img width="496" height="877" alt="image" src="https://github.com/user-attachments/assets/6119581b-946f-4955-9a2c-b25f2a939719" />

### 1. **SSH Login Evidence**

- Show the `auth.log` lines with attacker IP (`203.0.113.89`) and `Accepted password` for operator.
- Command & output to screenshot:

```bash
grep -R"203.0.113.89" evidence/var/log/auth.log
grep"Accepted" evidence/var/log/auth.log
```

<img width="1189" height="637" alt="image" src="https://github.com/user-attachments/assets/18b7d772-f872-40b9-b7fe-b262375f528d" />

**2. Malicious systemd Service**
`cat evidence/etc/systemd/system/phantom-agent.service`

<img width="977" height="519" alt="image" src="https://github.com/user-attachments/assets/e3b0601e-60ef-400d-b8d6-e64e00af3ef7" />

Key observations:

- disguised as **systemd‑network**
- starts a Python script
- designed to restart on failure

Important directive:

```
ExecStart=/usr/bin/python3 /opt/.hidden/agent.py
```

This references a missing file (`agent.py`) but clearly shows attacker intent to maintain persistence.

## 4. Hidden Directory Discovered

Directory:

```
/opt/.hidden
```

<img width="1007" height="178" alt="image" src="https://github.com/user-attachments/assets/0274ebf7-6c47-42a9-a2b1-e4bff81751c0" />

<img width="1191" height="622" alt="image" src="https://github.com/user-attachments/assets/10020e00-f8cb-4735-b566-3fae82508e89" />

## 5. 📡 Command‑and‑Control Configuration

Inside `exfil.py`:

```
C2_SERVER ="https://203.0.113.89:8443"
C2_AUTH_USER ="phantom_operator"
```

Meaning:

- C2 hosted on attacker IP
- HTTPS used (verify disabled)
- Basic auth login

---

## 6. Credential Encoding Method Recovered

Documented encoding process:

```
Base64(XOR(Hex(original),0x55 ) )
```

Actual implementation in script:

1. base64 decode value
2. XOR with `0x55`
3. output hex string
4. convert hex → ASCII (not implemented but required)

Note: script author forgot final hex→ASCII conversion, but readme confirms it.

---

## 7. Credential Decoding Process

Encoded credential from script:

```
Y2Z1ZmV1Ymd1Ymd1ZmZ1YzZ1ZmF1YmF1ZmR1ZmV1YzB1YDN1ZmR1YmZ1YDN1Yzd1ZmZ1Ymx1YDN1YmF1ZmV1YDN1Y2N1ZmV1Ymd1ZmZ1YzB1YmZ1ZmR1Y2Z1YmY=
```

Steps performed:

✔ base64 decode

✔ XOR each byte with `0x55`

✔ treat result as hex string

✔ convert to ASCII text

## 8. Recovered Attacker Operational Credentials

i used this script 

```php
 python3 - <<'EOF'
import base64, binascii, hashlib

enc = "Y2Z1ZmV1Ymd1Ymd1ZmZ1YzZ1ZmF1YmF1ZmR1ZmV1YzB1YDN1ZmR1YmZ1YDN1Yzd1ZmZ1Ymx1YDN1YmF1ZmV1YDN1Y2N1ZmV1Ymd1ZmZ1YzB1YmZ1ZmR1Y2Z1YmY="
raw = base64.b64decode(enc)

# XOR with 0x55
xored = bytes([b ^ 0x55 for b in raw])

# this gives hex string; convert to ASCII
hex_str = xored.decode()
password = bytes.fromhex(hex_str).decode()

print("Decoded password:", password)
print("SHA1:", hashlib.sha1(password.encode()).hexdigest())
EOF

Decoded password: c0rr3l4t10n_1s_k3y_t0_f0r3ns1cs
SHA1: 6dab44b1c788cbc90047abf48e36da4aa8431379
```

<img width="1193" height="344" alt="image" src="https://github.com/user-attachments/assets/eaac9c13-84c4-4973-88e5-d1ad7a5da046" />

### Username

```
phantom_operator
```

### Decoded Password

```
c0rr3l4t10n_1s_k3y_t0_f0r3ns1cs
```

### Optional hash verification

SHA1:
```
6dab44b1c788cbc90047abf48e36da4aa8431379
```
