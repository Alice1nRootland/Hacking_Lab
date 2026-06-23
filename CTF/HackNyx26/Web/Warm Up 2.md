<img width="560" height="460" alt="image" src="https://github.com/user-attachments/assets/f5b87485-8dc6-4c78-ad0c-e7cde968f0cb" />

#### Context Reconnaissance

To understand the immediate environment, we used MariaDB's XML parsing functions to force the backend to throw verbose XPATH errors containing our subquery outputs.

<img width="661" height="335" alt="image" src="https://github.com/user-attachments/assets/13cca937-e7c9-4170-be72-5fbd561df46b" />

- **Result:** Confirmed the active database context was **`shop_db`**.

We then dumped all tables within this active database:

<img width="781" height="337" alt="image" src="https://github.com/user-attachments/assets/bd7462c0-b9c3-438d-8da2-81b33cd1a0fd" />

- **Result:** Revealed only a single table: **`products`**.

#### Proving Absence in the Default Schema

To verify if the flag was simply an unlisted store item (e.g., `visible = 0`), we attempted to grep directly for the flag format (`HYNX`) across both text columns in the `products` table:

<img width="897" height="195" alt="image" src="https://github.com/user-attachments/assets/478e88b8-c40b-491b-a239-f9a408c2228a" />

- **Result:** The application loaded successfully but returned `No products found`. Because the syntax executed without throwing an SQL error, this mathematically proved that the string `HYNX` did not exist inside `shop_db`. The flag had to live in a completely different database on the same server.

#### Transitioning to UI Reflection (UNION Attack)

To bypass the strict 32-character limit of `extractvalue()`, we transitioned to a clean `UNION` attack. By testing with `ORDER BY`, we determined the backend query selected exactly **4 columns** (`id`, `name`, `description`, `price`).

We turned the store inventory UI into a live server mapping tool to list every database hosted on the instance:

**Payload:** 

`?search=' UNION SELECT 1, schema_name, 'Database Schema', 99.99 FROM information_schema.schemata -- -`

<img width="182" height="750" alt="image" src="https://github.com/user-attachments/assets/2da7a728-5a55-4958-94e5-cc5bec6f31f7" />

- **Result:** The store cards rendered the full backend architecture:
    - `shop_db`
    - `staging_users`
    - `employee_records`
    - `internal_logs`
    - `network_portal`
    - `admin_panel_backup`
    - **`test_db_do_not_use`**

#### Disarming the Rabbit Hole

The schema `test_db_do_not_use` immediately presented as a high-probability target. Further enumeration revealed a table named `test_creds` containing the columns `id, u, p, notes`.

However, when attempting to dump the credentials:

**Payload:** `?search=' UNION SELECT 1, concat('User: ', u, ' | Pass: ', p), notes, 99.99 FROM test_db_do_not_use.test_creds -- -`

<img width="445" height="142" alt="image" src="https://github.com/user-attachments/assets/28b026b3-c4e7-4520-9344-fa3d11be85e3" />

- **Result:** Only the original 5 store products rendered. `test_creds` was completely empty—a classic decoy placed by the author to waste time.

#### Global Column Hunting (The Silver Bullet)

Rather than manually crawling the remaining 5 custom databases, we executed a server-wide search against `information_schema.columns` to locate any column containing the substring `flag`:

**Payload:** `?search=' UNION SELECT 1, table_schema, concat(table_name, ' -> ', column_name), 99.99 FROM information_schema.columns WHERE column_name LIKE '%flag%' -- -`

<img width="640" height="757" alt="image" src="https://github.com/user-attachments/assets/a7b5e613-eb67-423b-a70f-a6e3c33b9eef" />

- **Result:** The storefront instantly printed the exact cross-database path to our target:
    - **Database Context:** `network_portal`
    - **Target Table:** `user`
    - **Target Column:** `flag`

#### Final Exfiltration

With the precise coordinates secured, we executed one final cross-database query to render the flag inside a shopping card:

**Payload:** `?search=' UNION SELECT 1, 'VICTORY!', flag, 99.99 FROM network_portal.user -- -`

<img width="532" height="427" alt="image" src="https://github.com/user-attachments/assets/30e35d36-053c-4ba7-b3eb-2f8f4cb1a638" />
