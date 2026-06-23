<img width="1352" height="385" alt="image" src="https://github.com/user-attachments/assets/157336de-05a5-45bb-8319-e987f62cc981" />

#### Reconnaissance & Service Fingerprinting

An initial service discovery scan was performed using `nmap` with default scripts and version detection logic to map the available attack surface:

<img width="772" height="382" alt="image" src="https://github.com/user-attachments/assets/f1ee2cb7-4f79-42d3-8f1a-9f45129b3f9f" />

| **Port** | **Status** | **Service** | **Version / Info** |
| --- | --- | --- | --- |
| **22/tcp** | Open | SSH | OpenSSH 8.0 (CentOS) |
| **80/tcp** | Open | HTTP | Apache httpd 2.4.37 (CentOS) — *Title: The Nocturnal Market* |
| **443/tcp** | Open | HTTP | Mongoose httpd — *Plain text listener* |
| **9090/tcp** | Closed | zeus-admin | — |

### Key Takeaways

1. **Port 80** hosts the target phishing web interface disguised as an online storefront selling security auditing gear.
2. **Port 443** initially flags as standard HTTPS space, but triggers critical protocol errors (`TLS connect error: unexpected eof`) when handled via SSL. Sending a raw unencrypted HTTP request manually reveals a backend API listener returning structural error packets in JSON format.

#### Web Content Enumeration

Automated directory brute-forcing was launched against the root web service on Port 80 using `ffuf` alongside common path wordlists to discover hidden endpoints or leftover administration folders:

<img width="755" height="626" alt="image" src="https://github.com/user-attachments/assets/9739ebb5-2110-4b98-acb1-e62d3617727b" />

The fuzzing run uncovered several interesting paths pointing to exposed directory indexes:

- `/settings/` (Contains a target `config.php` file yielding `HTTP 200` but rendering blank due to server-side execution).
- `/_admin/` (Contains an absolute instance of the SB Admin bootstrap template configuration, containing `dist/`, `src/`, and boilerplate script modules).

#### Vulnerability Analysis & API Interaction

Probing Port 443 with a clean HTTP status layout using fuzzing parameters reveals the structural API footprint of the **GhostDriver / PhantomJS headless browser automation engine**:

<img width="802" height="467" alt="image" src="https://github.com/user-attachments/assets/5af16421-9254-477e-a128-680889e208cf" />

#### Discovered API Endpoints

- `GET /status` — Confirms PhantomJS build version `1.2.0` on a Linux architecture.
- `GET /sessions` — Exposes active execution tracking blocks, yielding live session tokens:

```jsx
"id":"b5cd4920-6d35-11f1-8210-73b088c0c438","capabilities":{"browserName":"phantomjs","version":"2.1.1"}
```

#### Vulnerability Identification

PhantomJS 2.1.1 combined with GhostDriver 1.2.0 features an unauthenticated WebDriver protocol listener. This layout is vulnerable to **Arbitrary File Read / Server-Side JavaScript Injection**. By exploiting the proprietary `/phantom/execute` endpoint of an active session, an attacker can execute arbitrary code within the context of the PhantomJS instance via the native backend filesystem module (`fs`).

#### Exploitation & Flag Retrieval

Using the live session token (`b5cd4920-6d35-11f1-8210-73b088c0c438`), targeted JSON POST payloads were constructed to invoke PhantomJS's server-side environment libraries.

#### Foothold & Target Mapping

Reading `/etc/passwd` to enumerate localized users:

<img width="1522" height="252" alt="image" src="https://github.com/user-attachments/assets/1443c914-15b8-41c7-b636-5bbac65ea6bb" />

- **Discovery:** Revealed two primary local standard users: `moneygrabber` (UID 1000) and `admin` (UID 1001).

#### Locating the Web Context Flag (`www-data.txt`)

Checking inner web directories by listing files outside of the traditional server public HTML path via `fs.list()`:

<img width="1517" height="82" alt="image" src="https://github.com/user-attachments/assets/b38d6c6c-c9d9-4169-a280-3469e95d1781" />

The search target was discovered at `/var/www/www-data.txt`. Extracting its contents:

<img width="1517" height="82" alt="image" src="https://github.com/user-attachments/assets/b6b50768-3064-4646-9d77-ab4ba8c9ca3b" />

- **Flag String:** `HNYX{4ce8ade380c1516ee450f77462d9f457}`

#### Locating the User Flag (`user.txt`)

Pivoting directly to the home environment space of the mapped threat actor account:

<img width="1517" height="82" alt="image" src="https://github.com/user-attachments/assets/752d4cab-a521-41f7-aee5-e1b04863eac1" />

- **Flag String:** `HNYX{cbecc8e9c5c1bed8e7085cd45e675fe1}`

#### PrivEsc Analysis & Root Flag Compromise

A global environmental check was issued to analyze why the active engine process could comfortably cross standard privilege boundaries:

<img width="1517" height="125" alt="image" src="https://github.com/user-attachments/assets/4c252f49-6b39-4839-8fc3-38b03b567d54" />

The returned ecosystem structure flagged `"USER":"root"` and `"HOME":"/root"`.

#### Remediation Vulnerability Breakdown

The headless browser script runner on port 443 was misconfigured to launch natively as the **root administrative user**. This critical privilege isolation failure completely bypassed standard OS-level permissions. Consequently, the root space was readable directly via the ongoing arbitrary file readout hook:

<img width="1515" height="77" alt="image" src="https://github.com/user-attachments/assets/123bc0ed-f35c-4248-bb39-737d91b2daff" />

**Flag String:** `HNYX{ba9cdc68a113fa98cdac7f17caa6c571}`
****
