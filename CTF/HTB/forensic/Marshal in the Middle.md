<img width="697" height="639" alt="image" src="https://github.com/user-attachments/assets/00907432-ff34-4764-af0a-ee82739ed9ca" />

## Challenge Description

The security team was alerted to suspicious network activity from a production web server. The task was to determine if any data was stolen and identify what it was.

Given files:

- `chalcap.pcapng` → Network traffic capture
- `secrets.log` → TLS pre-master secrets log (for decrypting HTTPS traffic)
- Zeek logs (`bro/`) → Parsed traffic logs

<img width="769" height="350" alt="image" src="https://github.com/user-attachments/assets/93084caf-0ca6-4bf1-8f80-079190b9b884" />

## Step 1 — Initial Analysis

The provided packet capture (`chalcap.pcapng`) primarily contained encrypted TLS traffic. Since a **`secrets.log`** file was also given, this hinted that the HTTPS sessions could be decrypted to inspect the payload.

## Step 2 — Decrypting TLS Traffic

To decrypt HTTPS:

1. Opened Wireshark → `Edit → Preferences → Protocols → TLS`.
2. Loaded `secrets.log` into **(Pre)-Master-Secret log filename**.
3. Reopened the `chalcap.pcapng`.

<img width="837" height="627" alt="image" src="https://github.com/user-attachments/assets/bf34bc69-afa9-4de4-be2c-c09bef65e3ed" />

## Step 3 — Filtering for Exfiltrated Data

To focus only on decrypted application data, I applied the following display filter in Wireshark:

```
http.file_data contains "HTB"
```

This directly searched HTTP payloads for the string `HTB`, which is a common flag format.

<img width="1526" height="258" alt="image" src="https://github.com/user-attachments/assets/60cce12b-21a5-4f44-91b3-dacc3d41d921" />

## Step 4 — Identifying the Flag

After applying the filter, one packet contained suspicious outbound data with the flag string.

By inspecting the full decrypted HTTP payload (`Follow → TLS Stream`), the following flag was revealed:

<img width="848" height="836" alt="image" src="https://github.com/user-attachments/assets/f58e10e9-d0a4-416b-b4b6-5550e21bcd90" />

```php
HTB{Th15_15_4_F3nD3r_Rh0d35_M0m3NT!!}
```

boom thats our flag
