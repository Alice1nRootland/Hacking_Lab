<img width="699" height="642" alt="image" src="https://github.com/user-attachments/assets/4760e73a-8599-4b3a-be15-d38cb9a11837" />

start with some scanning 

<img width="903" height="262" alt="image" src="https://github.com/user-attachments/assets/a7520cf9-e6d8-4a40-afdb-3924cb4f4426" />

> What is the name of the FTP software running on Blocky?
> 

to identify the software i try ran as ftp since the nmap wont show the version 

```php
ftp 10.129.156.169
```

<img width="893" height="136" alt="image" src="https://github.com/user-attachments/assets/0dae3625-4fdb-44b2-a1a9-15c4fdfed1af" />

right away you can see the version **ProFTPD**

> What username is given by enumerating the website?
> 

<img width="1523" height="662" alt="image" src="https://github.com/user-attachments/assets/adda1cee-cadf-47e5-9603-56a3efefbe3f" />

then i went throught the site and navigate to author section and found **notch** as the username 

> What relative path on the webserver offers two JAR files for download?
> 

Next i try use gobuster to identify the hidden path 

```php
└─$ gobuster dir -u http://blocky.htb/ -w /usr/share/wordlists/dirb/common.txt -x php,txt,jar -t 40
```

<img width="904" height="741" alt="image" src="https://github.com/user-attachments/assets/5cf2df67-9b3e-47df-8f0e-f87aac82d43c" />

here is my finding then i try go each of the path so here what i find 

<img width="1534" height="448" alt="image" src="https://github.com/user-attachments/assets/66298474-5967-4f72-9ecf-9048f5a6332e" />

the answer is `/plugins`

> What password is present in the BlockCore.jar file?
> 

I Download the file and use 

### Credential Extraction from JAR

Downloaded and decompiled `BlockyCore.jar`:

<img width="905" height="571" alt="image" src="https://github.com/user-attachments/assets/28fc2496-ad0c-4b23-8257-fbd4bf022336" />

public String sqlPass = **"8YsqfCTnvxAUeduzjNSXe22";**

> Submit the flag located in the notch user's home directory.
> 

I log in as notch by ssh and use the password given

<img width="899" height="440" alt="image" src="https://github.com/user-attachments/assets/500749dc-bc29-4915-b48e-2b182b0405df" />

right away you found the flag 

> Submit the flag located in root's home directory.
> 

Then i right away use `sudo -i` command and log in as root

<img width="903" height="214" alt="image" src="https://github.com/user-attachments/assets/d065d22a-b548-42d0-8137-7210916a005b" />
