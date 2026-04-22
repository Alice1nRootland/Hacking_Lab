# CTF Write-up: Nexus (User Flag)

## **Reconnaissance**

The initial scan revealed a standard web server and an SSH service. While the web portal looked like the primary entry point, it was designed to be "AI-resistant," effectively stalling automated tools.

<img width="951" height="480" alt="image" src="https://github.com/user-attachments/assets/ff4aa0cb-7d38-4de9-ac05-d1f8385edfb6" />

- **Port 22:** Open (SSH)
- **Port 80:** Open (HTTP - Apache 2.4.52)

## **Enumeration**

#### **The Web Portal**

Navigating to the homepage revealed **Nexus Solutions**, an IT services company. The page content provided a critical hint:

> *"Our lead administrator... believes in the classic 'pen and paper' methods for absolute security—sometimes an offline note is better than an online password manager. Have a look at their pristine setup!"*
> 

<img width="960" height="726" alt="image" src="https://github.com/user-attachments/assets/6c419fe4-dd04-49aa-a458-a24e5dab6e26" />

This directed focus to an image located at `/images/desk.png`.
****

### **The "Vision-Based" Clue**

<img width="959" height="735" alt="image" src="https://github.com/user-attachments/assets/462f5019-56c8-4a49-a578-22eff4f943ed" />

Examination of `desk.png` (the "Admin Cave") revealed the administrator's desk. High-resolution analysis of the image showed:

- **The Monitor:** A text editor showing source code for a binary.
- **The Notebook:** Handwritten notes containing potential credentials and "Emergency Protocols."
- **Hidden String:** A set of credentials was visible in the corner of the notebook: `nexus : N3xus!2026`.

## **Exploitation & Initial Access**

### **Credential Discovery with Hydra**

While the password was clearly visible in the image, the associated username was not. To avoid manual lockout or "tarpit" delays, a targeted credential spray was performed against the SSH service using a list of common system usernames.

<img width="953" height="269" alt="image" src="https://github.com/user-attachments/assets/b89866de-17dc-4843-9fe7-cb98bc514808" />

**Results:**

> `[22][ssh] host: 192.168.0.50   login: nexus   password: N3xus!20261 of 1 target successfully completed, 1 valid password found`
> 

### **Initial Shell Access**

Using the validated credentials, an SSH session was established as the user `nexus`.

<img width="749" height="363" alt="image" src="https://github.com/user-attachments/assets/c8145429-d722-4403-acfe-bc572aae7fe1" />

## **Retrieving the User Flag**

Upon landing in the user's home directory, the environment was found to be highly hardened (no `sudo`, `strace`, or `ltrace` available). However, the user flag was readable within the directory

<img width="632" height="37" alt="image" src="https://github.com/user-attachments/assets/9da4b3b8-85b0-44ae-b50c-7e28456cb3d1" />

<img width="729" height="71" alt="image" src="https://github.com/user-attachments/assets/f04f2076-78bf-4cc3-a2c9-9c3cacf2c80d" />

**User Flag:** `hack10{h0n3yp0ts_4r3_v1s10n_b4s3d}`
