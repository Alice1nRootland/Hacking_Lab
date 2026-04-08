# Kobold - HTB Writeup (Part 1: Initial Foothold)

**Target IP:** `10.129.245.50`**Attacker IP:** `10.10.15.71` (Kali `tun0`)

### 1. Reconnaissance

#### Initial Nmap Scan

We begin by scanning the target to identify open ports and running services.

<img width="775" height="241" alt="image" src="https://github.com/user-attachments/assets/5ae97ec9-cd1f-4b70-a347-4e8f82e2dcc2" />

**Key Findings:**

- **Port 22:** OpenSSH
- **Port 80/443:** Nginx Web Server (Redirects to `kobold.htb`)

### 2. Subdomain Enumeration (VHost Fuzzing)

Since the main page is a decoy, we need to find the hidden subdomains. We use Virtual Host fuzzing to ask the server if specific subdomains exist.

#### Finding the Baseline

First, we check the response size of a non-existent subdomain so we know what to ignore:

```sql
curl -s -k -I https://10.129.245.50 -H "Host: doesntexist.kobold.htb" | grep "Content-Length"
```

<img width="827" height="68" alt="image" src="https://github.com/user-attachments/assets/54885516-f69c-4811-a29a-62168795d82a" />

The server returns a default size of **154 bytes**.
****

### Fuzzing with ffuf

We use `ffuf` with a standard wordlist to discover valid subdomains, using the `-fs 154` flag to filter out the baseline responses.

<img width="1164" height="510" alt="image" src="https://github.com/user-attachments/assets/92c8c786-5eb7-42a9-aa2d-a6df94e39531" />

**Results:**

- `bin` (Size: 24402)
- `mcp` (Size: 466)

We update our `/etc/hosts` file with the newly discovered targets:

```sql
echo "10.129.245.50 kobold.htb mcp.kobold.htb bin.kobold.htb" | sudo tee -a /etc/hosts
```

<img width="849" height="69" alt="image" src="https://github.com/user-attachments/assets/6e18e0af-5b34-4556-a5c7-3847730c5788" />

### 3. Vulnerability Discovery

Navigating to `https://mcp.kobold.htb`, we find the **MCPJam Inspector** dashboard exposed without authentication. Exploring the UI (specifically the Settings tab) reveals the software version: **v1.4.2**.

<img width="1276" height="667" alt="image" src="https://github.com/user-attachments/assets/56413c26-1f59-4c8d-9c9a-783ad1324be3" />

A quick search for "MCPJam Inspector 1.4.2 exploit" leads to a GitHub Advisory detailing **CVE-2026-23744**.

<img width="1281" height="750" alt="image" src="https://github.com/user-attachments/assets/b24c281f-d29c-499c-8099-7c1205a6a8f1" />

- **The Flaw:** The application exposes an API endpoint (`/api/mcp/connect`) meant for local testing to the entire network (`0.0.0.0`).
- **The Impact:** It accepts a JSON payload containing commands to run an "MCP Server" but executes them without any validation, leading to Unauthenticated Remote Code Execution (RCE).

### 4. Exploitation (Getting a Shell)

We can exploit the `/api/mcp/connect` endpoint to force the server to send us a reverse shell.

#### Step 1: Start the Listener

On the Kali machine, we set up a Netcat listener to catch the connection:

<img width="275" height="46" alt="image" src="https://github.com/user-attachments/assets/3747cea3-058f-4e99-ad4c-4437e0976e53" />

#### Step 2: Send the Payload

In a new terminal, we use `curl` to send a malicious JSON POST request containing a standard bash reverse shell payload pointing back to our Kali IP.

<img width="823" height="179" alt="image" src="https://github.com/user-attachments/assets/8c44f60e-799e-49b3-8343-9f0a4400d2de" />

#### Step 3: Capture

Switching back to the `nc` listener, we catch the reverse shell as the user **ben**

we can now navigate to Ben's home directory and read the user flag

<img width="1072" height="147" alt="image" src="https://github.com/user-attachments/assets/3ef7982e-759b-406c-95a9-4336a59df4b0" />

## Part 2: Privilege Escalation

### 1. User Enumeration

After securing the initial shell and stabilizing it with `pty`, the first step is to understand the privileges assigned to our current user, **ben**.

<img width="721" height="53" alt="image" src="https://github.com/user-attachments/assets/ed75a5d6-e161-433d-acd2-524341fffbc7" />

We immediately notice that `ben` belongs to a non-standard group called **`operator`**. To see what this group has access to, we search the filesystem for files owned by it:

<img width="963" height="226" alt="image" src="https://github.com/user-attachments/assets/1f43c71b-34c1-4e72-8a60-4f19faa9143e" />

This reveals write access to a shared Docker volume used by the PrivateBin container. While this could be used for a complex Local File Inclusion (LFI) chain, there is a more direct path to `root`.
****

### **2. The Docker Group Secret**

In Linux, the `/etc/gshadow` file can assign group privileges that do not explicitly appear in the standard `id` output. On Kobold, the `operator` group has been secretly granted access to the **`docker`** group.

We can verify this by using the `sg` (switch group) command to ask the Docker daemon for a list of running containers:

<img width="1176" height="70" alt="image" src="https://github.com/user-attachments/assets/62c011d4-e3d4-4c0d-905c-bba5f735ee03" />

The daemon responds successfully, confirming we have full Docker privileges.
****

### 3. The Container Escape (Root)

Membership in the `docker` group is effectively equivalent to `root` access. Because the Docker daemon runs as root, we can instruct it to spin up a new container and mount the host machine's physical hard drive inside of it.

We execute a "one-shot" container escape using the locally cached `privatebin` image:

```sql
sg docker -c 'docker run --rm -u 0 -v /:/hostfs --entrypoint cat privatebin/nginx-fpm-alpine:2.0.2 /hostfs/root/root.txt'
```

**Command Breakdown:**

- **`sg docker -c`**: Bypasses the current shell's group restrictions and runs the command with Docker permissions.
- **`docker run --rm`**: Starts a temporary container that cleans up after itself.
- **`u 0`**: Forces the container process to run as `root` (UID 0), bypassing file read restrictions.
- **`v /:/hostfs`**: Maps the real host's root directory (`/`) to the `/hostfs` directory inside the container.
- **`-entrypoint cat`**: Overrides the container's default web server script, instructing it to simply `cat` the target file.

The container successfully boots, reaches into the host's filesystem, and prints the final flag:

<img width="1350" height="69" alt="image" src="https://github.com/user-attachments/assets/a15f268a-af25-49ed-bfae-df94d35c07c3" />

**Root Flag:** `b0061150d780fcc68a293fa0e78fbf45`
