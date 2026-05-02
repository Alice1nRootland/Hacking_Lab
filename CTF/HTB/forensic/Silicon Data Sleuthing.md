<img width="700" height="648" alt="image" src="https://github.com/user-attachments/assets/e7957adb-d2cd-42f6-b852-4913332df637" />

# OpenWrt Router Firmware Forensics — Lab Writeup

**Goal:** Extract useful configuration and secrets from a router firmware image (chal_router_dump.bin) and document commands, findings, and screenshot suggestions so someone else can reproduce the work.We were given a raw router firmware image containing multiple partitions (uImage kernel, SquashFS rootfs, and a JFFS2 overlay). The tasks were to discover the OpenWrt version, Linux kernel, root password hash, PPPoE credentials, Wi‑Fi SSID and password, and WAN→LAN DNAT ports.

> *What version of OpenWRT runs on the router (ex: 21.02.0)*
> 

Identify Embedded Filesystems with `binwalk`

```php
binwalk chal_router_dump.bin
```

<img width="1543" height="429" alt="image" src="https://github.com/user-attachments/assets/9844cd6a-94e5-4363-a322-b209ea734b43" />

This scanned the binary for known signatures and revealed:

- Multiple **JBOOT headers** (custom bootloader format)
- A **U-Boot version string** (`U-Boot 1.1.3`)
- A **uImage kernel** (`OpenWrt Linux-5.15.134`)
- A **SquashFS filesystem** (offset: `0x42C2C8`)
- A **JFFS2 filesystem** (offset: `0x7C0000`)

Extract Filesystems with `binwalk -e`

```php
binwalk -e chal_router_dump.bin
```

<img width="1551" height="730" alt="image" src="https://github.com/user-attachments/assets/106f7315-6a52-418e-91a6-4a856a9b263e" />

This attempted to extract embedded filesystems automatically. You hit a few snags:

- **Missing** `sasquatch`: This tool is needed to extract SquashFS with non-standard compression (e.g., xz).
- **Missing** `jefferson`: Needed for JFFS2 extraction.
- **Symlink warnings**: Binwalk redirected unsafe symlinks to `/dev/null` for security.

Despite the warnings, binwalk successfully extracted:

- `squashfs-root`: the main root filesystem
- `jffs2-root`: persistent storage (though extraction failed due to missing `jefferson`)

Inspect Extracted Filesystem

```php
cat squashfs-root/etc/openwrt_release 2>/dev/null || true
```

<img width="1532" height="316" alt="image" src="https://github.com/user-attachments/assets/9bac2108-75d1-4b07-a4e5-a05e13976080" />

This confirmed the firmware is:

- **OpenWrt 23.05.0**
- Target: `ramips/mt7621` (MIPS-based SoC)
- Architecture: `mipsel_24kc`

Answer: **23.05.0**

> *What is the Linux kernel version (ex: 5.4.143)*
> 

Run these first — often they immediately show the version.

1. `strings` + `grep` (very quick)

```php
strings chal_router_dump.bin | grep -i "openwrt" | head -n 50
```

<img width="775" height="109" alt="image" src="https://github.com/user-attachments/assets/ddf1ffaa-9584-44ae-af2c-5a0a13644840" />

Answer: **5.15.134**

> *What's the hash of the root account's password, enter the whole line (ex: root:$2$JgiaOAai....)*
> 

**Prereqs**

- Kali (or similar) with `binwalk`, `squashfs-tools` and Python3.
- `jefferson` for JFFS2 extraction (install inside a venv as shown).

**Minimal, exact steps**

1. Create and activate a Python venv and install `jefferson` (one-time):

```bash
python3 -m venv ~/jefferson-env
source ~/jefferson-env/bin/activate
pip install jefferson
```

(You only need to run the venv steps once; afterward just `source ~/jefferson-env/bin/activate`.)

1. Identify partitions with `binwalk` (confirm where SquashFS / JFFS2 live):

```bash
binwalk chal_router_dump.bin
```

Look for lines indicating `Squashfs filesystem` and `JFFS2 filesystem`. Note their offsets (binwalk prints them).

1. Carve out the JFFS2 partition (use the offset from binwalk; example offset was `0x7C0000` = `8126464`):

```bash
dd if=chal_router_dump.bin of=fs.jffs2 bs=1 skip=8126464 status=progress
file fs.jffs2
```

`file` confirms it’s a JFFS2 image.

1. Extract JFFS2 with `jefferson` (this writes a `jffs2-root/` directory):

```bash
jefferson fs.jffs2
ls -la jffs2-root
```

You should see `upper/` and `work/` entries; often `upper/sysupgrade.tgz` will be present.

1. List the tarball contents (if present) to see what files are inside the overlay:

```bash
tar -tzf jffs2-root/upper/sysupgrade.tgz | sed -n '1,200p
```

Look for `etc/shadow`, `etc/passwd`, `etc/config/*`, etc.

1. Extract `/etc/shadow` from the sysupgrade tarball (to a temp directory) and check it:

```bash
mkdir -p /tmp/jffs2_extract
tar -xzf jffs2-root/upper/sysupgrade.tgz -C /tmp/jffs2_extract ./etc/shadow 2>/dev/null || true
sed -n '1,200p' /tmp/jffs2_extract/etc/shadow 2>/dev/null || true
```

If it prints nothing, the shadow might exist elsewhere in the dump—search the entire `jffs2-root` tree next.

1. Grep the entire extracted JFFS2 dump for any `root:` lines (fast and reliable):

```bash
grep -R --line-number '^root:' jffs2-root 2>/dev/null || true
```

This finds *all* files containing a `root:` line across `upper/` and `work/`. In this firmware the relevant entry was inside a `work/work/#32` file produced by `jefferson`.

1. Narrow the search to hash-like patterns (common hash prefixes `$1$`, `$6$`, `$2y$`, etc.):

```bash
grep -R --line-number -E '^root:[^:]*\$[126y]\$|^root:[^:]*\$2[aby]\$' jffs2-root 2>/dev/null || true
```

This helps ignore simple `root:x` or empty-root entries and shows the file containing the actual hash.

<img width="785" height="398" alt="image" src="https://github.com/user-attachments/assets/da2de8e4-8cf0-48ae-b39e-4ea5025e86d4" />

Answer: **root:$1$YfuRJudo$cXCiIJXn9fWLIt8WY2Okp1:19804:0:99999:7:::**

> *What is the PPPoE username*
> 

**Quick checklist (confirm extraction)**

```bash
# show the important dirs
ls -la squashfs-root     # read-only factory files
ls -la jffs2-root        # overlay (upper/ and work/)
ls -la jffs2-root/upper  # often contains sysupgrade.tgz
```

**Why:** PPP and Wi-Fi overrides are often in the overlay (`jffs2-root/upper/sysupgrade.tgz` or inside `work/`

<img width="804" height="439" alt="image" src="https://github.com/user-attachments/assets/0135351e-a665-4df4-844d-94aefaf19632" />

**Inspect overlay tarball (common place)**

```bash
# list contents of sysupgrade.tgz (if present)
tar -tzf jffs2-root/upper/sysupgrade.tgz | sed -n '1,200p'
```

Look for: `etc/config/network`, `etc/config/wireless`, `etc/ppp/chap-secrets` or `etc/shadow`.

<img width="797" height="517" alt="image" src="https://github.com/user-attachments/assets/53e865de-22e3-4943-98a5-1e5a2c028ced" />

**Extract the relevant files to a temp directory**

```bash
mkdir -p /tmp/jffs2_extract
tar -xzf jffs2-root/upper/sysupgrade.tgz -C /tmp/jffs2_extract \
    ./etc/config/network ./etc/config/wireless ./etc/ppp/chap-secrets ./etc/ppp/pap-secrets 2>/dev/null || true
```

**Why:** Extract only the files we need to inspect safely.

**PPPoE username & password**

Common places:

- `/etc/config/network` (OpenWrt style `option username` / `option password`)
- `/etc/ppp/chap-secrets` or `pap-secrets`
- If `option username '...'` found → the username string.

```php
grep -R --line-number -iE 'pppoe|ppp|chap-secrets|pap-secrets|option username' squashfs-root jffs2-root 2>/dev/null || true
```

<img width="804" height="152" alt="image" src="https://github.com/user-attachments/assets/11c19a9a-3a68-4c85-b209-1c352220c235" />

Answer: **yohZ5ah**

> *What is the PPPoE password*
> 

If `option password '...'` found → submit the password string.

```php
 grep -R --line-number -iE "option password|option key|password|chap-secrets|pap-secrets" squashfs-root jffs2-root 2>/dev/null || true
```

<img width="800" height="236" alt="image" src="https://github.com/user-attachments/assets/af5c2afd-d853-44c1-856d-a97a93404110" />

Answer: **ae-h+i$i^Ngohroorie!bieng6kee7oh**

> *What is the WiFi SSID*
> 

Primary file: `/etc/config/wireless` (or inside the overlay tarball)

```php
grep -R --line-number "option ssid" squashfs-root/etc/config/wireless jffs2-root 2>/dev/null || true
```

<img width="790" height="114" alt="image" src="https://github.com/user-attachments/assets/c2dff768-f679-401a-9b45-6992ab3fae77" />

- SSID string found after `option ssid` (example: `VLT-AP01`)

> *What is the WiFi Password*
> 

check both read-only rootfs and overlay
`grep -R --line-number -iE "option key|option psk|wpa_passphrase|option encryption" squashfs-root jffs2-root 2>/dev/null || true`

<img width="799" height="200" alt="image" src="https://github.com/user-attachments/assets/eabc2e03-9f60-4026-b63a-586366ca4abd" />

• Wi-Fi password from `option key` (example: `french-halves-vehicular-favorable`)

> *What are the 3 WAN ports that redirect traffic from WAN -> LAN (numerically sorted, comma sperated: 1488,8441,19990)*
> 

Search firewall config or any redirect blocks in the overlay:

```php
grep -R --line-number -i "redirect" squashfs-root jffs2-root 2>/dev/null || true
```

<img width="802" height="144" alt="image" src="https://github.com/user-attachments/assets/3706ddda-e573-4d67-9cc0-03fab3a9d795" />

Each `config redirect` block will contain `option src 'wan'` and `option src_dport 'NNNN'` — the `src_dport` values are the WAN ports being redirected to LAN.

```php
 grep -A 10 -i "config redirect" jffs2-root/work/work/#b
```

<img width="801" height="320" alt="image" src="https://github.com/user-attachments/assets/a5479fc0-1c15-43d4-af0d-b6d4d56645bd" />

- `DB` → `src_dport '1778'`
- `WEB` → `src_dport '2289'`
- `NAS` → `src_dport '8088'`

These are the **WAN-side ports** that accept incoming traffic and redirect it internally to LAN destinations.

Answer: **1778,2289,8088**

by submitting that last questions we will get our  flag

**Tools**

- `binwalk`, `strings`, `dd`, `unsquashfs` / `squashfs-tools`, `jefferson`, `tar`, `grep`, `sed`, `awk`.

**What I did (high level)**

1. `binwalk` + `strings` to locate embedded images (uImage, SquashFS, JFFS2).
2. Extracted SquashFS (`unsquashfs` / `binwalk -e`) and read `/etc` for OpenWrt info.
3. Carved JFFS2 (offset from binwalk), extracted it with `jefferson`.
4. Listed and inspected `jffs2-root/upper/sysupgrade.tgz` (tarball) and `jffs2-root/work/*` fragments.
5. Grepped extracted files for `root:`, `option username`, `option password`, `option ssid`, `option key`, and `config redirect` to get exact values.

**Exact files checked**

- `squashfs-root/etc/openwrt_release`, `/etc/banner` (OpenWrt version)
- `uImage` header / `strings` (kernel version)
- `jffs2-root/upper/sysupgrade.tgz` → `etc/shadow`, `etc/config/network`, `etc/config/wireless`
- `jffs2-root/work/...` (jefferson-produced fragments)
- `jffs2-root` firewall fragments for `config redirect` blocks

**Key commands (one-liners)**

- `binwalk chal_router_dump.bin`
- `dd if=chal_router_dump.bin of=fs.jffs2 bs=1 skip=<offset>`
- `jefferson fs.jffs2`
- `tar -tzf jffs2-root/upper/sysupgrade.tgz`
- `tar -xzf jffs2-root/upper/sysupgrade.tgz -C /tmp/extract ./etc/shadow ./etc/config/network ./etc/config/wireless`
- `grep -R --line-number '^root:' jffs2-root`
- `grep -R --line-number -iE 'option ssid|option key|option username|option password|config redirect' jffs2-root /tmp/extract squashfs-root`

**Results (answers you submitted)**

- **OpenWrt version:** (found in `/etc/openwrt_release`) — *you discovered it earlier*
- **Kernel version:** `5.15.134`
- **Root `/etc/shadow` line:**
    
    `root:$1$YfuRJudo$cXCiIJXn9fWLIt8WY2Okp1:19804:0:99999:7:::`
    
- **PPPoE username:** `yohZ5ah`
- **PPPoE password:** `ae-h+i$i^Ngohroorie!bieng6kee7oh`
- **Wi-Fi SSID:** `VLT-AP01`
- **Wi-Fi Password:** `french-halves-vehicular-favorable`
- **WAN→LAN redirect ports (sorted):** `1778,2289,8088`
- **Flag obtained:** `HTB{Y0u'v3_m4st3r3d_0p3nWRT_d4t4_3xtr4ct10n_4nd_c0nf1g!!}`
