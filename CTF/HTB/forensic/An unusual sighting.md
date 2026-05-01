<img width="693" height="644" alt="image" src="https://github.com/user-attachments/assets/09a005f8-b290-4f39-a66c-bfb25b5c1f66" />

<img width="849" height="63" alt="image" src="https://github.com/user-attachments/assets/fd456cce-b578-4de1-8823-dfa5f738e0bc" />

<img width="821" height="36" alt="image" src="https://github.com/user-attachments/assets/4c583fd5-240f-48f6-83fb-d9c069b8dd66" />

<img width="844" height="80" alt="image" src="https://github.com/user-attachments/assets/e79ca95e-b134-47c1-900e-5bbb5846cb04" />

<img width="827" height="85" alt="image" src="https://github.com/user-attachments/assets/05765999-d1bf-490d-b3ab-d50f721a4906" />

<img width="960" height="40" alt="image" src="https://github.com/user-attachments/assets/8c0cae7a-7674-40ae-b0cd-a16d1265086f" />

all this we can see on sshd.log 

<img width="833" height="72" alt="image" src="https://github.com/user-attachments/assets/17f7b5dd-048f-4041-a458-9d4ad026cf36" />

<img width="953" height="19" alt="image" src="https://github.com/user-attachments/assets/647f4a9e-f484-4c7b-9a23-3a7e1cfe566b" />

from bash_history.txt 

<img width="847" height="114" alt="image" src="https://github.com/user-attachments/assets/d412e609-b38e-4d62-a806-c6ec29d3e63f" />

<img width="968" height="29" alt="image" src="https://github.com/user-attachments/assets/e52ba8dc-ecc7-4bf8-a02e-e920db26ddc5" />

```php
HTB{4n_unusual_s1ght1ng_1n_SSH_l0gs!} 
```

---

## Step-by-Step Guide: How to Read SSH Logs

### 1. **Understand the Log Format**

SSH logs typically follow this structure:

Code

`[YYYY-MM-DD HH:MM:SS] <log message>`

Each line includes:

- **Timestamp**: When the event occurred
- **Message**: What happened (connection, authentication, command, etc.)

Example:

Code

`[2024-02-19 04:00:14] Accepted password for root from 2.67.182.119 port 60071 ssh2`

### 2. **Identify Key Event Types**

Here are the most common log messages and what they mean:

| Log Message Type | Meaning |
| --- | --- |
| `Server listening on ...` | SSH service started and is ready |
| `Connection from <IP>` | Someone tried to connect |
| `Failed publickey/password for ...` | Authentication attempt failed |
| `Accepted password for ...` | Successful login |
| `Starting session: shell ...` | Shell session began |
| `Disconnected from user ...` | User logged out or session ended |

### 3. **Track a Full Session**

To analyze a full login session, follow this sequence:

1. **Connection initiated**
    
    Code
    
    `Connection from 2.67.182.119 port 60071`
    
2. **Authentication attempts**
    
    Code
    
    `Failed publickey for root ...
    Accepted password for root ...`
    
3. **Session start**
    
    Code
    
    `Starting session: shell on pts/2 ...`
    
4. **Commands executed** (from `bash_history.txt`)
    
    Code
    
    `whoami  
    uname -a  
    ./setup`
    
5. **Session end**
    
    Code
    
    `Disconnected from user root ...`
    

### 4. **Spot Suspicious Behavior**

Look for patterns that stand out:

- **Unusual login times** (e.g. 04:00 AM)
- **Rare IP addresses** (only appear once)
- **Use of** `root` **account**
- **Failed logins followed by success**
- **Commands like** `wget`**,** `shred`**,** `setup`—often used in attacks

### 5. **Correlate with Bash History**

If you have access to `bash_history.txt`, match timestamps with logins to see what the user did after logging in.

Example:

Code

`[2024-02-19 04:00:14] Accepted password for root ...
[2024-02-19 04:00:18] whoami
[2024-02-19 04:14:02] ./setup`

This shows the attacker logged in, checked privileges, downloaded a file, and ran a setup script
