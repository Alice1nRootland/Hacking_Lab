<img width="497" height="891" alt="image" src="https://github.com/user-attachments/assets/7dd866b2-4af2-4483-966a-447b92a4eb27" />

## 1. Reconnaissance

We started by navigating to the target application at `http://5.223.57.169:40859/`.
The website presented a "Service Status Dashboard" with simple HTML and no apparent interactive functionality (no login forms on the home page, static content).

However, the challenge description hinted at a "rushed deployment" and "cut corners." In web challenges, this often points to left-over backup files or exposed version control directories.

We performed a manual check for a hidden **.git** directory, which is a common misconfiguration when developers clone repositories directly into the public web root (`/var/www/html`) without denying access to hidden folders.

**Command:**

<img width="1076" height="212" alt="image" src="https://github.com/user-attachments/assets/9a473a47-0f1c-4784-96af-c48470769479" />

**Result:**
The server returned `HTTP 200 OK`. This confirmed that the `.git` directory was accessible to the public.

## 2. Vulnerability Analysis

**Vulnerability:** Information Disclosure (Exposed `.git` Directory).

When a `.git` folder is exposed, an attacker can download the entire repository, including:

- **Source Code:** Backend logic (Python, PHP, Node.js, etc.).
- **Commit History:** Previous versions of files (where deleted secrets often live).
- **Configuration Files:** Hardcoded credentials, API keys, or database passwords.

In this scenario, Nginx was configured to serve static files but failed to block access to the `/.git/` path.

---

## 3. Exploitation (Repository Extraction)

Since directory listing was disabled (we couldn't just browse the files in a browser), we used `git-dumper` to blindly reconstruct the repository by downloading Git objects one by one.

**Tools Used:** `git-dumper` (Python)

**Exploitation Steps:**

1. **Install Tool:** `pip3 install git-dumper`
2. **Create Loot Directory:** `mkdir git_loot`
3. **Dump Repository:**

<img width="1539" height="632" alt="image" src="https://github.com/user-attachments/assets/455cd9bc-2d3c-4659-bf1b-9f673467a1a6" />

**Inspect Files:**
Once the download finished, we entered the directory.

<img width="1272" height="202" alt="image" src="https://github.com/user-attachments/assets/0a23f921-3116-423b-8597-ffa065998574" />

We found a Python Flask application structure: `app.py`, `templates/`, `static/`, and the fully reconstructed `.git` folder.

4. Code Analysis & Credential Discovery

We examined the main application file, `app.py`, to understand how the authentication works.

**Command:**

Bash

`cat app.py`

<img width="1381" height="538" alt="image" src="https://github.com/user-attachments/assets/8b45b56c-08a8-4054-9ead-ba0b119fd771" />

`RE:CTF{g1t_3xp0sur3_l34ds_t0_cr3d_l34k}`
