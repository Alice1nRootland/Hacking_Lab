#### **CTF Write-Up: Transfer (Boot2Root)**

#### Reconnaissance & Enumeration

We kick things off with a standard `nmap` scan to map out the open ports and running services.

<img width="1513" height="637" alt="image" src="https://github.com/user-attachments/assets/e1cacff3-2c85-47a1-9d45-d0322be54f0a" />

**Nmap Results:**

- **Port 21 (FTP):** vsftpd 3.0.5 - Anonymous FTP login is explicitly allowed.
- **Port 22 (SSH):** OpenSSH 8.2p1 Ubuntu.

The anonymous FTP access is our primary target for initial enumeration.

#### Initial Access

I connected to the FTP server using the `anonymous` login.

<img width="767" height="551" alt="image" src="https://github.com/user-attachments/assets/789a8bb9-646e-45e9-9846-8dcd70e7705f" />

A quick `ls` revealed three interesting files. I grabbed them all using the `get` command:

1. `employee_ssh` (An RSA Private Key)
2. `note.txt` (A message from the admin)
3. `user.txt` (The user flag)

<img width="1253" height="667" alt="image" src="https://github.com/user-attachments/assets/1dce04a0-b8dd-4a99-ba58-c291bb876ff7" />

Reading `user.txt` immediately gave us our first flag:
**User Flag:** `HNYX{AN0N_M1SC0NF1G_FTP}`

Next, I analyzed `note.txt` to gather context on the target environment:

```jsx
Hey stephen,
I noticed you keep losing your login credentials. I've left a copy of your private SSH key here temporarily. Please download it and delete it immediately.
- WhiteUsagi (Network Admin)
```

The note suggests the SSH key belongs to a user named `stephen`. Before attempting to connect, I secured the private key permissions:

<img width="266" height="47" alt="image" src="https://github.com/user-attachments/assets/deb3d473-fec1-49eb-ab7b-b6397f4b0678" />

#### The Misdirection Trap

Attempting to log in as `stephen` using the key resulted in a password prompt, meaning the server rejected the key.

Running the connection in verbose mode (`ssh -v`) confirmed the key was offered but explicitly denied. However, looking at the filename itself (`employee_ssh`), I suspected a classic CTF misdirection. The note was addressed to `stephen`, but the key was intended for a service account named `employee`.

Switching the username to `employee` resulted in a successful connection:

<img width="662" height="438" alt="image" src="https://github.com/user-attachments/assets/b4393673-4ee4-42e6-b0c7-a7c30a7afd3f" />

#### We now have a local shell as `employee`.

Privilege Escalation to Root

With local access secured, the goal shifted to vertical privilege escalation. Standard checks like `sudo -l` failed due to requiring a password we didn't possess. I moved on to enumerating file permissions, specifically looking for files owned by `employee` outside the home directory.

<img width="690" height="243" alt="image" src="https://github.com/user-attachments/assets/39579ace-d08b-45ec-a445-a5a673c42d24" />

This query returned a highly suspicious file: `/opt/cleanup.sh`.

Checking the permissions of this file revealed a major security flaw:

```jsx
ls -la /opt/cleanup.sh
-rwxr--r--  1 employee employee   74 Jun 10 09:48 cleanup.sh
```

The file is completely writable by our low-privileged `employee` account. Inspecting the script revealed it was a placeholder for log cleanup:

<img width="312" height="62" alt="image" src="https://github.com/user-attachments/assets/d57d7ae9-179d-4c05-b6a3-82b863c0647f" />

#### Hijacking the Cron Job

Scripts placed in `/opt` and executed without a visible `crontab` entry often point to a hidden root-level cron job. To verify this, I appended a harmless tracking command to the script to see who was executing it:

After waiting exactly one minute, I checked `/tmp/cron_test.txt`. The file appeared, and the contents simply read: `root`.

#### The SUID Payload

Since `root` is executing whatever we place inside `/opt/cleanup.sh` every minute, I wiped the file and injected a payload to copy the system bash binary into `/tmp` and grant it SUID permissions. This is a cleaner persistence method than a reverse shell.

<img width="887" height="38" alt="image" src="https://github.com/user-attachments/assets/2a46073e-8557-4fb3-8043-730e9a7ceec8" />

I set up a quick bash loop to monitor `/tmp` and wait for the SUID binary to be compiled by the automated cron task:

<img width="1300" height="85" alt="image" src="https://github.com/user-attachments/assets/0be53443-2c46-42a8-96d0-785dd96e6c5a" />

Once the file appeared with the `-rwsr-sr-x` permissions, I executed it with the `-p` flag to preserve the inherited root privileges:

<img width="332" height="77" alt="image" src="https://github.com/user-attachments/assets/abd0e1ec-35ad-4593-a6ac-5f6e2b47c1a1" />

**Root Flag:** `HNYX{CR0NTAB_P3RM_3SCALATE_B2R1}`
****
