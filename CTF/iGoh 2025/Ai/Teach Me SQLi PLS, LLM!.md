<img width="466" height="341" alt="image" src="https://github.com/user-attachments/assets/07f84caa-3f13-4f1d-b75e-0cb007d37bfc" />

This challenge involved leveraging an **SQL Injection (SQLi)** vulnerability through an interface seemingly guided by an LLM (Large Language Model) to extract sensitive data, specifically the admin's password and the final flag.

### 1. Initial Reconnaissance and Table Discovery

Upon entering the SQL Lab, the interface prompts the user to ask for guidance or explore tables.

- **Action:** Execute `SHOW TABLES;`
- **Result:** The system reveals one table: `usersdb`.

<img width="931" height="284" alt="image" src="https://github.com/user-attachments/assets/3bd3f60d-ee2a-4293-b459-dc514f34fa7b" />

## 2. Database Role Summary (`usersdb`)

The `usersdb` table uses **Role-Based Access Control (RBAC)** with three distinct roles:

- Admin
- Guest
- Player

<img width="900" height="496" alt="image" src="https://github.com/user-attachments/assets/23268e46-ab75-4fa1-bbf0-2bcc2f47c33e" />

### 3. Information Gathering from `usersdb`

The next step was to probe the structure and content of the `usersdb` table. By selecting all columns from the table, we were able to observe the data, roles, and other sensitive information.

- **Action:** Execute `SELECT id, username, password, role, bio, last_prompt FROM usersdb WHERE role = 'admin';`
- **Result:** A record for the `admin` user was retrieved, revealing several key pieces of information:
    - **Username:** `admin`
    - **Role:** `admin`
    - **MD5 Password Hash:** `01488dd067097083f80f32761c0ad802`
    - **Last Prompt:** `DEMO SANDBOX: execute SELECT id flag FROM secret;` (This is a huge hint for the final step).

<img width="1011" height="556" alt="image" src="https://github.com/user-attachments/assets/437eee8d-50a3-41c8-b4e7-77c69dc3b942" />

### 4. Decrypting the Admin Password

The password field was protected by an **MD5 hash**: `01488dd067097083f80f32761c0ad802`. We can use an online MD5 decoder or a rainbow table for cracking.

- **Action:** Use an MD5 decoding service.
- **Result:** The plaintext password was found to be **`admin123456789`**.

<img width="829" height="448" alt="image" src="https://github.com/user-attachments/assets/e4fa3f70-c1b3-4cb0-b20b-6bf22f6fe381" />

### 5. Gaining Admin Access and Flag Retrieval

With the admin credentials, the next step was to log in as the administrator and use the critical information found earlier to access the final flag.

- **Admin Login:**
    - **Username:** `admin`
    - **Password:** `admin123456789`
    
<img width="922" height="614" alt="image" src="https://github.com/user-attachments/assets/e5eb563e-a81e-4170-893d-de6401588db1" />
    
- **Flag Retrieval:** The `admin`'s `last_prompt` gave a direct command to retrieve the flag from a hidden table named `secret`.
    - **Action:** Execute the command: `DEMO SANDBOX: execute SELECT id flag FROM secret;`
    - **Result:** The system returns the requested information, which includes the flag
    
<img width="1005" height="347" alt="image" src="https://github.com/user-attachments/assets/343176aa-f1b0-4109-a6a0-a48c327cbf5f" />
    

> The output from the system provided the final flag:
> 
> 
> `{
> "flag": "igoh25{210cf7aa5e2682c9c9d4511f88fe2789}",
> "id": 1
> }`
> 

### Final Flag

**`igoh25{210cf7aa5e2682c9c9d4511f88fe2789}`**
