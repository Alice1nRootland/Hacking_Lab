<img width="703" height="642" alt="image" src="https://github.com/user-attachments/assets/b8cb39c3-1b54-4a24-b95e-1aa17021fc51" />

- Full webroot snapshot at `html/` (provided by challenge).
- Key directories inspected:
    - `html/wp-content/plugins/plugin-manager/` (malicious plugin)
    - `html/wp-blogs/2022/11/` (phishing kit)
    - `html/wp-content/themes/maintheme/` (custom theme)
    - `html/wp-content/uploads/2022/11/` (phishing assets)
- Files referenced in findings: `wp-config.php`, `.htaccess`, `plugin-manager.php` (decoded), `index.php` under `wp-blogs`.

```php
echo "[*] Show plugin-manager.php (first 200 lines)"; sed -n '1,200p' html/wp-content/plugins/plugin-manager/plugin-manager.php
```

<img width="1525" height="631" alt="image" src="https://github.com/user-attachments/assets/02535d02-ae73-4b7f-94b8-bb5476504135" />

by decoding this base64 you will get the first half flag

<img width="1286" height="180" alt="image" src="https://github.com/user-attachments/assets/33e608b7-a16b-4353-a379-71b9c0e4b93a" />

**Malicious plugin with reverse shell**

- Path: `html/wp-content/plugins/plugin-manager/plugin-manager.php`
- Function: a PHP reverse shell that spawns `/bin/sh -i` and connects to `77.74.198.52` on port `4444`.
- Contains part of challenge flag: `part1 = "HTB{C0m3_0n"`.
- This plugin gives an attacker command-line access to the host as the web process user, enabling full remote control and file operations

**Phishing landing / payload drop**

- Path: `html/wp-blogs/2022/11/index.php` contained obfuscated JavaScript which decodes a base64 blob, XORs it with a key, and causes the browser to download `official_invitation.iso`.
- The ISO contains `official_invitation.exe`. Extracting strings from that EXE revealed `part2`. The final flag assembled from both parts:

`HTB{C0m3_0n_1t_w4s_t00_g00d_t0_b3_tru3}`
