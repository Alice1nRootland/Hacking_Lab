<img width="879" height="554" alt="image" src="https://github.com/user-attachments/assets/ff702667-13f4-42aa-b5da-5f9dc7d45b53" />

# **Machine Write-up: Principal**

**Difficulty:** Medium

**OS:** Linux

**Focus:** Cryptographic Trust Flaws (JWT/JWE & SSH CA)

## **1. Reconnaissance**

We began with a standard service scan to identify open ports and versions.

```jsx
nmap -sC -sV 10.129.50.204
```

<img width="921" height="781" alt="image" src="https://github.com/user-attachments/assets/ca335280-0779-4b68-a154-748dd075a1c6" />

**Key Findings:**

- **Port 22:** OpenSSH 9.6p1
- **Port 8080:** Jetty Web Server
- **Version Disclosure:** `X-Powered-By: pac4j-jwt/6.0.3`

The `pac4j-jwt/6.0.3` version is specifically vulnerable to **CVE-2026-29000**, an authentication bypass where the system trusts the contents of an encrypted JWE even if the inner JWT is unsigned (`alg: none`).

## 2. Web Enumeration

After discovering an open web port, the goal was to identify the specific technologies in use and find any documentation or client-side code that explains the authentication logic.

**1. Header Analysis (The "Fingerprint")**

By running `curl -v http://10.129.50.204:8080/login`, we analyzed the HTTP response headers. One header in particular stood out as a critical vulnerability marker:

<img width="990" height="771" alt="image" src="https://github.com/user-attachments/assets/a211a2f5-29aa-422c-828c-baaab8d6156a" />

> **Finding:** `X-Powered-By: pac4j-jwt/6.0.3`
> 
- **Significance:** This identifies the exact library used for session management. In a real-world or CTF scenario, this allows an attacker to search for specific **CVEs**.
- **Vulnerability:** Version **6.0.3** is specifically susceptible to **CVE-2026-29000**. This flaw allows for an authentication bypass by wrapping an unsigned "Plain" JWT inside a valid JWE (Encrypted) envelope.

**2. JavaScript Discovery (`app.js`)**
While examining the HTML body of the login page, we found a reference to a script: `<script src="/static/js/app.js"></script>`. Analyzing this file provided the "blueprint" of the entire application’s security architecture.
****

<img width="987" height="376" alt="image" src="https://github.com/user-attachments/assets/f03e6d54-93ec-474c-9943-b0009eb6bdbf" />

#### **A. Internal API Endpoints**

The script explicitly listed the following routes, which are usually hidden from unauthenticated users:

- `JWKS_ENDPOINT = '/api/auth/jwks'`: The location of the public keys.
- `USERS_ENDPOINT = '/api/users'`: A management page for user data.
- `SETTINGS_ENDPOINT = '/api/settings'`: The system configuration page.

<img width="988" height="792" alt="image" src="https://github.com/user-attachments/assets/bf5d6e6b-0928-4889-a06f-08361d7ab0e7" />

#### **B. Encryption & Token Details**

The comments in `app.js` provided the exact cryptographic parameters needed to build a malicious token:

- **Type:** JWE (JSON Web Encryption).
- **Key Encryption:** `RSA-OAEP-256`.
- **Content Encryption:** `A128GCM`.
- **Inner Token Algorithm:** `RS256` (this is what we targeted by switching it to `none`).

#### **C. Role Hierarchy**

The script defined three roles: `ROLE_ADMIN`, `ROLE_MANAGER`, and `ROLE_USER`. Since we saw that only `ROLE_ADMIN` has access to the `/api/settings` and `/api/users` endpoints, our goal was set: **Forge a token with the `ROLE_ADMIN` claim.**

## 3. Exploitation (Initial Foothold via JWT Forgery)

This stage focuses on exploiting **CVE-2026-29000** in `pac4j-jwt`. The objective is to bypass authentication and gain access to the internal dashboard by impersonating an administrator.
****

### **The Vulnerability: JWT "None" Algorithm Confusion**

In many JWT implementations, the `alg: none` header tells the server that the token has no signature and should be trusted as-is. Secure systems disable this, but this specific vulnerability is more subtle:

1. The server uses **JWE (JSON Web Encryption)** to hide the session token.
2. The server correctly decrypts the "outer envelope" using its RSA private key.
3. Once decrypted, it finds an "inner" JWT.
4. Because the *decryption* was successful, the server incorrectly assumes the *content* is also authentic, allowing us to use `alg: none` for the inner token.

#### **1. Gathering the Cryptographic Material**

To wrap our forged token, we first need the server's public key. We retrieved this from the `/api/auth/jwks` endpoint identified in Step 2.

<img width="986" height="258" alt="image" src="https://github.com/user-attachments/assets/5ca3bf64-4816-42ef-864b-da91788148a6" />

#### **2. Crafting the "Russian Doll" Token**

We used a Python script to automate the forgery. The process involves two distinct cryptographic steps:

- **Step A (The Core):** Create a standard JWT with the `alg: none` header. We set the `sub` (subject) to `admin` and the `role` to `ROLE_ADMIN`.
- **Step B (The Mask):** Encrypt that insecure JWT into a valid JWE envelope using the RSA public key we gathered.

```jsx
import json
import base64
import time
from jwcrypto import jwk, jwe

def base64url_encode(data):
    if isinstance(data, dict):
        data = json.dumps(data).encode()
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

# RSA Public Key from JWKS
public_key_dict = {
    "kty": "RSA",
    "e": "AQAB",
    "kid": "enc-key-1",
    "n": "lTh54vt..." # Replace with full 'n' from JWKS
}
key = jwk.JWK(**public_key_dict)

# Current timestamp for May 2026
now = int(time.time())

# 1. Create the Inner "Plain" JWT (Unsigned)
header = {"alg": "none", "typ": "JWT"}
payload = {
    "sub": "admin",
    "role": "ROLE_ADMIN",
    "iss": "principal-platform",
    "iat": now,
    "exp": now + 3600
}

inner_jwt = f"{base64url_encode(header)}.{base64url_encode(payload)}."

# 2. Encrypt the inner JWT into a JWE (Compact Serialization)
jwe_token = jwe.JWE(
    inner_jwt.encode('utf-8'),
    recipient=key,
    protected={
        "alg": "RSA-OAEP-256",
        "enc": "A128GCM",
        "kid": "enc-key-1"
    }
)

print(jwe_token.serialize(compact=True))
```

#### **Exfiltrating System Configurations (`/api/settings`)**

Using the forged admin token, a request was made to the `/api/settings` endpoint. This revealed the internal architecture and a high-value credential.

<img width="991" height="796" alt="image" src="https://github.com/user-attachments/assets/a4a503b7-351f-45b5-b18a-a1496b622a93" />

**Key Findings from Response:**

- **Credential Leak:** The `encryptionKey` was found to be `D3pl0y_$$H_Now42!`. In many environments, such keys are reused as passwords for service accounts.
- **Infrastructure Insight:** The `notes` field explicitly mentions that **SSH certificate authentication** is used for automation and points to `/opt/principal/ssh/` for the CA (Certificate Authority) configuration. This provided a clear path for privilege escalation.

### **Target User Identification (`/api/users`)**

To utilize the discovered credential, the user list was enumerated to identify which account would most likely be used for "deployments" or "automation."

<img width="986" height="828" alt="image" src="https://github.com/user-attachments/assets/bfb4523a-7017-45d6-910e-094e4506d0a4" />

**Analysis of User Data:**
The response returned a list of 8 users, but one entry was of particular interest:

- **Username:** `svc-deploy`
- **Role:** `deployer`
- **Note:** *"Service account for automated deployments via SSH certificate auth."*

This confirmed that `svc-deploy` was the intended target for the SSH foothold. The password found in the settings (`D3pl0y_$$H_Now42!`) matched the context of this service account perfectly.

## **4.Privilege Escalation (Abusing SSH Certificate Authority Trust)**

After gaining a foothold, the final objective was to escalate privileges from a service account to **root**. This phase exploits the machine’s namesake: **Principal** confusion within an SSH Certificate Authority (CA) environment.

#### **1. Establishing the Foothold**

Using the credentials harvested from the web dashboard (`svc-deploy` : `D3pl0y_$$H_Now42!`), an SSH connection was established.

<img width="763" height="645" alt="image" src="https://github.com/user-attachments/assets/a0a24e1b-1aeb-4dfe-9de7-a708aabf7eb2" />

Upon logging in, the **user.txt** flag was retrieved.

**Capture:**`0b4aa05a396cbe0b0aeb4ebe41d801da`

#### **2. Local Enumeration & Finding the "Crown Jewels"**

Standard enumeration (`sudo -l`) showed that the `svc-deploy` user has no sudo permissions. However, checking group memberships revealed that the user belongs to the `deployers` group.

<img width="808" height="152" alt="image" src="https://github.com/user-attachments/assets/53ce787f-2d8f-484e-ba0e-9cf93ff3e825" />

Recalling the infrastructure notes from the web dashboard, the directory `/opt/principal/ssh/` was inspected.

**Discovery**

The directory contains the **SSH CA private key** (named `ca`). Crucially, the permissions allow the `deployers` group to read this file. This key is used by the system to sign SSH certificates for automated tasks.

#### **3. The Exploit: Forging a Root Certificate**

SSH CA authentication works by trusting any key signed by a specific CA. The vulnerability here is that if an attacker possesses the CA private key, they can sign their own keys and specify any **"principal"** (username) they want—including **root**.

**A. Generate a local key pair**

A temporary Ed25519 key pair was generated in `/tmp`.

<img width="828" height="294" alt="image" src="https://github.com/user-attachments/assets/63e96ae4-7948-43ed-8d9f-48e373fe4760" />

**B. Sign the public key as "root"**

Using the stolen CA private key, the new public key was signed. The `-n root` flag is the exploit vector, as it identifies the certificate holder as the root user.

<img width="962" height="39" alt="image" src="https://github.com/user-attachments/assets/46e54b1f-5575-4817-8834-94a12aaed91a" />

• **Result:** A new file, `/tmp/exploit_key-cert.pub`, was created. The server will now recognize the corresponding private key as belonging to root.

## **5. Gaining Root Access**

The final step was to use the forged certificate and its private key to authenticate as root via SSH to the local interface.

<img width="988" height="279" alt="image" src="https://github.com/user-attachments/assets/097ef74f-3b8a-4bf9-8ddf-c95326c29103" />

The server accepted the forged certificate, granted a root shell, and the final flag was captured.

**Root Flag:**`8ec66bb9d4e2736d93cef0b536ffc5ab`
