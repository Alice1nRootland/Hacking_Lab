<img width="503" height="814" alt="image" src="https://github.com/user-attachments/assets/2573106c-be8f-4d5a-a117-3dd8614c80e7" />

## 1. Reconnaissance & Enumeration

### Network Scanning

The attack began with a full TCP port scan using **Nmap** to identify the attack surface:

<img width="741" height="617" alt="image" src="https://github.com/user-attachments/assets/e80d2d96-46a4-4f10-aa63-a27b7c5ef78a" />

**Key Findings:**

- **Port 21 (FTP):** vsFTPd 3.0.5 with **Anonymous login allowed**.
- **Port 22 (SSH):** OpenSSH 8.9p1 (Ubuntu).
- **Port 80 (HTTP):** Apache 2.4.52.
- **Port 8080 (HTTP):** Nginx 1.18.0 (potential proxy).

### FTP Enumeration

Seeing anonymous FTP access, I logged in to check for sensitive files:

<img width="888" height="648" alt="image" src="https://github.com/user-attachments/assets/897acfe1-17f6-441b-80d1-13839f36e386" />

Inside the `public` directory, a hidden file was discovered: `.secret_note.txt`.

### Credential Harvesting

Downloading and reading `.secret_note.txt` revealed a message from the Admin to a "new librarian":

<img width="555" height="250" alt="image" src="https://github.com/user-attachments/assets/59439b95-061f-4e69-a96a-7e559866cd54" />

> *Please use the password 'Shhh!KeepQuiet' for your local SSH account.*
> 

Based on the context of the machine name (**Library**) and the note's recipient, the username was identified as **`librarian`**.

## 2. Exploitation & Initial Foothold

### SSH Authentication

Using the harvested credentials, I attempted to gain a shell via SSH:

- **Username:** `librarian`
- **Password:** `Shhh!KeepQuiet`

<img width="672" height="512" alt="image" src="https://github.com/user-attachments/assets/6ea2ffd7-785d-4d8f-9c73-10b0d3ca81eb" />

the decode using 64
<img width="586" height="522" alt="image" src="https://github.com/user-attachments/assets/a73630f0-e306-43f7-a214-df1351363303" />


## 1. Local Enumeration

### System Investigation

After gaining initial access as the `librarian` user, I checked for standard privilege escalation vectors.

- **`sudo -l`**: The user was not in the sudoers file.

<img width="653" height="60" alt="image" src="https://github.com/user-attachments/assets/72321b8e-d159-4a4e-bf3f-3751f9aafa22" />

### Cron Job Analysis

Checking the system-wide crontab revealed a highly privileged automated task:

<img width="1001" height="408" alt="image" src="https://github.com/user-attachments/assets/4a6f197a-a02d-41e6-bdf9-74a6e4384a8e" />

**Finding:** A cron job was set to run every minute as the **root** user:
`* * * * * root /root/backup.sh`

While the script `/root/backup.sh` was not readable, its existence suggested a backup routine. Given the machine's theme and the existence of a `~/books` directory in the librarian's home folder, I hypothesized that the script was using `tar` with a wildcard to archive the contents of that directory.

## 2. Vulnerability Analysis: Tar Wildcard Injection

The vulnerability occurs when a command like `tar -cf backup.tar *` is executed by a high-privilege user in a directory where a low-privilege user has write access.

Unix shells expand the wildcard (`*`) into a list of filenames. If a filename starts with a dash (e.g., `--checkpoint=1`), `tar` interprets that filename as a **command-line flag** rather than a file to be archived.

## 3. Exploitation

### Step 1: Payload Creation

I created a shell script named `rootme.sh` designed to set the **SUID (Set User ID)** bit on the system's Bash binary. This would allow any user to execute Bash with the permissions of the file owner (root).

<img width="918" height="40" alt="image" src="https://github.com/user-attachments/assets/ad6921ba-31d5-4abc-8f5e-25f7b2f574f6" />

### Step 2: Injecting Malicious Flags

I created two empty files in the `~/books` directory named specifically to be interpreted as `tar` options:

<img width="970" height="53" alt="image" src="https://github.com/user-attachments/assets/e50596c3-00e7-472b-8062-5541640f50ec" />

- `-checkpoint=1`: Tells `tar` to show progress messages every 1 record.
- `-checkpoint-action`: Tells `tar` to execute a specific command when a checkpoint is reached.

## 4. Capturing the Flag

### Gaining Root Access

After waiting 60 seconds for the cron job to trigger, I verified that the SUID bit had been successfully applied to the Bash binary:

<img width="973" height="150" alt="image" src="https://github.com/user-attachments/assets/45032713-e605-4164-942e-a810f0d5492d" />

I then spawned a shell with root privileges:

<img width="820" height="332" alt="image" src="https://github.com/user-attachments/assets/747e2d13-e2e6-4dac-a519-19ae9ea2d722" />

then decode using b64

<img width="519" height="496" alt="image" src="https://github.com/user-attachments/assets/3f6d2385-5c0e-418f-a63b-a5406df135f8" />

**Root Flag:** `hack10{cr0n_t4r_w1ldc4rd_1nj3ct10n_ftw}`
