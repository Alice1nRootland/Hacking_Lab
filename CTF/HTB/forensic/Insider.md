<img width="698" height="643" alt="image" src="https://github.com/user-attachments/assets/d282a7f1-d007-40f1-bf50-26753f7030cd" />

While investigating the supplied archive, I extracted a Firefox profile and used a safe decryption tool (`firefox_decrypt`) to recover saved login credentials. The decryptor revealed a Tomcat Manager credential for `http://acc01:8080` (username `admin`, password `HTB{ur_8RoW53R_H157Ory}`).

I then corroborated the origin of the credential by inspecting three independent artifacts inside the same profile:

1. **sessionstore (recovery.jsonlz4)** — shows recorded tabs/entries for `/manager/html`.
2. **browser history (places.sqlite)** — contains `http://acc01:8080/manager` and related URLs.
3. **cookies (cookies.sqlite)** — contains a `JSESSIONID` cookie for host `acc01` and path `/manager`.

These artifacts demonstrate that the credential was used to access the Tomcat manager from this profile, validating provenance of the recovered flag.

### Unzip the provided archive

Explain: extract the archive to recover the Firefox profile files.

```bash
cd ~/Desktop/htb/Insider
unzip Insider.zip
# Note: if the archive is password-protected, unzip will prompt for it (you typed it earlier).
```

What to capture for writeup: list the extracted profile tree, e.g.

```bash
ls -la Mozilla/Firefox/Profiles/2542z9mo.default-release | sed -n '1,200p'
```

<img width="1576" height="790" alt="image" src="https://github.com/user-attachments/assets/76c3ce0d-a230-47d2-aa80-e33e8e8fab5c" />

this shows files like `logins.json`, `key4.db`, `places.sqlite`, `sessionstore-backups/recovery.jsonlz4` etc.

### Locate the profile containing saved logins

 find `logins.json` to confirm the profile to analyze.

```bash
find . -type f -name logins.json -print -exec dirname {} \;
```

<img width="1542" height="263" alt="image" src="https://github.com/user-attachments/assets/694a556e-dbf7-4ffb-9f8d-6d919c2a1bf8" />

### Work on a copy (do not modify original)

Explain: copy the profile to `/tmp` so we don’t alter evidence.

```bash
PROFILE="./Mozilla/Firefox/Profiles/2542z9mo.default-release"
cp -a "$PROFILE" /tmp/ff-profile-copy
# verify the copy contains the required files
ls -l /tmp/ff-profile-copy/{logins.json,key4.db,places.sqlite} 2>/dev/null || echo "some files missing"
```

<img width="1606" height="187" alt="image" src="https://github.com/user-attachments/assets/f754e69b-e6f6-4ae0-8daa-e2fea63d9aa9" />

### Get (or clone) the firefox_decrypt tool

Explain: we’ll use an existing, maintained script to decode Firefox logins.

```bash
# if you haven't already
git clone https://github.com/unode/firefox_decrypt.git ~/tools/firefox_decrypt
cd ~/tools/firefox_decrypt
# ensure Python deps / system tools exist
sudo apt update
sudo apt install -y libnss3-tools
pip3 install pyasn1 pycryptodome lz4
```

<img width="1580" height="518" alt="image" src="https://github.com/user-attachments/assets/1f530109-4631-402d-a83b-645bdcd97e5c" />

### Run the decryptor against the copied profile

Explain: this script uses `key4.db` + NSS data to decrypt the saved login blobs in `logins.json`.

```bash
# run from the repo directory
python3 firefox_decrypt.py /tmp/ff-profile-copy
```

Notes:

- If the profile uses a Firefox primary/master password the script will prompt for it. If none was set, press Enter.
- The script prints each site, username and password it recovered.

<img width="1579" height="187" alt="image" src="https://github.com/user-attachments/assets/38deb347-9abd-45a5-94cb-b64a29efae09" />

## Conclusion

The recovered credential (`admin` / `HTB{ur_8RoW53R_H157Ory}`) comes from a saved Firefox login in the provided profile. The session store, browsing history, and cookies all show `http://acc01:8080/manager` activity from the same profile, confirming provenance and validating the flag.
