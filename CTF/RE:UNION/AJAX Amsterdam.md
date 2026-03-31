<img width="497" height="629" alt="image" src="https://github.com/user-attachments/assets/950b3cf8-dbdb-477e-8336-c3e4d55b3e6d" />

GIVEN FILE 
<img width="1587" height="487" alt="image" src="https://github.com/user-attachments/assets/5786cd37-f481-472c-93f8-af788b3e54ff" />
### A. Source Code Review

Upon reviewing `ajax-amsterdam.php`, two critical flaws were identified:

1. **Insecure AJAX Handler (`aaf_remote_loader`):**
The code takes the `rid` (Review ID) parameter from the GET request and concatenates it directly into a SQL query without sanitization or prepared statements.PHP
    
    `$rid = $_GET['rid']; 
    // VULNERABLE: Direct concatenation
    $query = "SELECT player_name, critique FROM $table_name WHERE id = " . $rid;`
    
2. **Weak Access Control:**
The security check relies solely on the HTTP User-Agent header.PHP
    
    `if ($_SERVER['HTTP_USER_AGENT'] !== 'F-Side') { die("Access Denied"); }`
    

### Step 1: Access Verification

Standard requests were blocked. We spoofed the User-Agent to `F-Side` to interact with the API.

### Step 2: SQL Injection & Filter Bypass

We confirmed the injection using a `UNION SELECT`.

<img width="1594" height="107" alt="image" src="https://github.com/user-attachments/assets/c4f7b0f5-c4aa-487f-b315-86f523476226" />

- **Attempt 1 (Failed):** We tried to select the `aaf_admin_token` using standard SQL syntax: `WHERE option_name='aaf_admin_token'`. The server responded with "Data not found", indicating that **Single Quotes (`'`) were being stripped or filtered**, causing the query to fail.
- **Attempt 2 (Success):** We used **Hex Encoding** to represent the string `aaf_admin_token` without using quotes.
    - `aaf_admin_token` -> `0x6161665f61646d696e5f746f6b656e`
    
<img width="1598" height="107" alt="image" src="https://github.com/user-attachments/assets/e907a16f-18c6-4c42-968c-64276833117e" />
    

### Step 3: Flag Retrieval

Using the SQL injection, we extracted the maintenance token and submitted it to the `aaf_sys_maintenance` endpoint to retrieve the flag.
<img width="1594" height="107" alt="image" src="https://github.com/user-attachments/assets/1c1c659e-4ca6-4428-a8d9-e1e4b913f3e4" />

`RE:CTF{ezchainingunauthsqli2bac_oleeoleee}`
