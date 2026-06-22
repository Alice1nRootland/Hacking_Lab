#### **CTF Write-Up: Transfer (Boot2Root)**

#### Reconnaissance & Enumeration

We kick things off with a standard `nmap` scan to map out the open ports and running services.


<img width="767" height="551" alt="image" src="https://github.com/user-attachments/assets/e3e4cf1b-6c23-4e1b-a54f-078c9eab87e9" />


**Nmap Results:**

- **Port 21 (FTP):** vsftpd 3.0.5 - Anonymous FTP login is explicitly allowed.
- **Port 22 (SSH):** OpenSSH 8.2p1 Ubuntu.

The anonymous FTP access is our primary target for initial enumeration.

#### Initial Access

I connected to the FTP server using the `anonymous` login.

<img width="1513" height="637" alt="image" src="https://github.com/user-attachments/assets/befa2e87-0b93-4e65-94c8-b48a1b0b4f64" />


A quick `ls` revealed three interesting files. I grabbed them all using the `get` command:

1. `employee_ssh` (An RSA Private Key)
2. `note.txt` (A message from the admin)
3. `user.txt` (The user flag)

<img width="1253" height="667" alt="image" src="https://github.com/user-attachments/assets/23e45e8d-30f5-4ad0-b311-f59e6a809d37" />


Reading `user.txt` immediately gave us our first flag:
**User Flag:** `HNYX{AN0N_M1SC0NF1G_FTP}`

Next, I analyzed `note.txt` to gather context on the target environment:

```jsx
Hey stephen,
I noticed you keep losing your login credentials. I've left a copy of your private SSH key here temporarily. Please download it and delete it immediately.
- WhiteUsagi (Network Admin)
```

The note suggests the SSH key belongs to a user named `stephen`. Before attempting to connect, I secured the private key permissions:

<img width="266" height="47" alt="image" src="https://github.com/user-attachments/assets/8a6ae2c7-df77-4076-af8a-bf326593629e" />

#### The Misdirection Trap

Attempting to log in as `stephen` using the key resulted in a password prompt, meaning the server rejected the key.

Running the connection in verbose mode (`ssh -v`) confirmed the key was offered but explicitly denied. However, looking at the filename itself (`employee_ssh`), I suspected a classic CTF misdirection. The note was addressed to `stephen`, but the key was intended for a service account named `employee`.

Switching the username to `employee` resulted in a successful connection:

<img width="662" height="438" alt="image" src="https://github.com/user-attachments/assets/e4cdcd4c-213f-4831-a3d1-de9d1aeb9acb" />


#### We now have a local shell as `employee`.

Privilege Escalation to Root

With local access secured, the goal shifted to vertical privilege escalation. Standard checks like `sudo -l` failed due to requiring a password we didn't possess. I moved on to enumerating file permissions, specifically looking for files owned by `employee` outside the home directory.

<img width="690" height="243" alt="image" src="https://github.com/user-attachments/assets/e1e7d3c7-cad0-4faf-a6d7-7233aac77b27" />


This query returned a highly suspicious file: `/opt/cleanup.sh`.

Checking the permissions of this file revealed a major security flaw:

```jsx
ls -la /opt/cleanup.sh
-rwxr--r--  1 employee employee   74 Jun 10 09:48 cleanup.sh
```

The file is completely writable by our low-privileged `employee` account. Inspecting the script revealed it was a placeholder for log cleanup:

<img width="312" height="62" alt="image" src="https://github.com/user-attachments/assets/ab409370-5220-4c20-b557-5d1a1ac2e58e" />

#### Hijacking the Cron Job

Scripts placed in `/opt` and executed without a visible `crontab` entry often point to a hidden root-level cron job. To verify this, I appended a harmless tracking command to the script to see who was executing it:

After waiting exactly one minute, I checked `/tmp/cron_test.txt`. The file appeared, and the contents simply read: `root`.

#### The SUID Payload

Since `root` is executing whatever we place inside `/opt/cleanup.sh` every minute, I wiped the file and injected a payload to copy the system bash binary into `/tmp` and grant it SUID permissions. This is a cleaner persistence method than a reverse shell.

<img width="887" height="38" alt="image" src="https://github.com/user-attachments/assets/caa3a21b-3c3d-40dd-a6ab-fdd1057a1e52" />

I set up a quick bash loop to monitor `/tmp` and wait for the SUID binary to be compiled by the automated cron task:

<img width="1300" height="85" alt="image" src="https://github.com/user-attachments/assets/507db371-a2f1-4967-bdfb-85144067fb8b" />

Once the file appeared with the `-rwsr-sr-x` permissions, I executed it with the `-p` flag to preserve the inherited root privileges:

<img width="332" height="77" alt="image" src="https://github.com/user-attachments/assets/062b21ef-8303-429a-b0d1-c24a639ad816" />

**Root Flag:** `HNYX{CR0NTAB_P3RM_3SCALATE_B2R1}`
****
