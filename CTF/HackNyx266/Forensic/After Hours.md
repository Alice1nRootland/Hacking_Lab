<img width="625" height="642" alt="image" src="https://github.com/user-attachments/assets/589030dc-3ef2-4de3-8fc3-bafbdd444d0b" />

#### Bypassing Disk Image Corruption

We began our analysis by verifying the file structure of the provided compressed file `disk.img.gz`.

<img width="337" height="167" alt="image" src="https://github.com/user-attachments/assets/a93c17d5-5822-4e53-abdd-b5fe73bb6808" />


**Output:** `disk.img: data`

Because `file` returned generic `data`, it indicated that the standard Master Boot Record (MBR) or partition definitions at the beginning of the block storage were destroyed. We ran `binwalk` to scan for raw filesystem headers embedded further down the image:

<img width="1356" height="123" alt="image" src="https://github.com/user-attachments/assets/5fa8289d-54c0-4e9e-8200-c157ef397899" />


The output revealed that a healthy Linux `ext4` filesystem partition was sitting at exactly a **1 MB offset (`0x100000`)**. The first 1 MB of the disk had been completely zeroed out to masquerade as corrupted data.

We extracted the clean filesystem chunk using `dd`:

<img width="573" height="100" alt="image" src="https://github.com/user-attachments/assets/aa851416-fdb2-46d5-92a8-0ac584174a3f" />


**Output:** `extracted_fs.img: Linux rev 1.0 ext4 filesystem data...`

#### Uncovering the Decoy & Memory Clues

With a mountable ext4 partition extracted, we mounted it onto our Kali system to browse the operating system architecture:

<img width="390" height="86" alt="image" src="https://github.com/user-attachments/assets/1242fa14-519f-421a-a106-6cdedcaf6c24" />


<img width="1010" height="476" alt="image" src="https://github.com/user-attachments/assets/b92cedfa-fee5-4c75-89d6-a1e6122cdd79" />


Inside the temporary file systems directory (`/tmp/.flag`), we located a decoy flag file containing an MD5-like string:`HNYX{74ccdaf686bb385d2b54e56b3426bda0}`

However, the file also contained an explicit warning log indicating anti-forensics operations:

<img width="1007" height="367" alt="image" src="https://github.com/user-attachments/assets/c912bc69-5ba8-436c-8b9d-d427c98679d7" />


```jsx
rm /etc/.auditd.tmp
history -c
Cleanup happened after audit rotation. File content is not inside the mounted filesystem.
Dec 01 16:42:01 gateway sshd[1042]: Accepted password for root
Dec 01 16:49:12 gateway auditd[1337]: rotated segment s2 at 0x06200000
Dec 01 16:49:18 gateway auditd[1337]: rotated segment s0 at 0x06000000
Dec 01 16:49:29 gateway auditd[1337]: rotated segment s3 at 0x06300000
Dec 01 16:49:41 gateway auditd[1337]: rotated segment s1 at 0x06100000
Dec 01 16:50:23 gateway ash[1401]: command cleanup completed
```

#### Analysis of the Log Clue:

The attacker cleared the bash history (`history -c`) and deleted operational configurations. However, the Linux Audit Daemon (`auditd`) managed to record the exfiltration events before terminating, rotating memory logging segments directly to precise physical disk offsets:

- **s0** at `0x06000000`
- **s1** at `0x06100000`
- **s2** at `0x06200000`
- **s3** at `0x06300000`

#### Raw Memory Carving

Since the data bypassed the regular filesystem tables, we returned to our original raw `disk.img` file to extract these exact 1 MB rotated slots using `dd`:

<img width="577" height="397" alt="image" src="https://github.com/user-attachments/assets/6703a8fe-3722-42f4-a74d-99559bdd502a" />


Running `file` and `binwalk` directly against these carved `.bin` images yielded nothing but empty space flags, meaning standard printable ASCII log layouts weren't present. We inspected the raw layout via `xxd`, dropping the null spaces:

<img width="566" height="315" alt="image" src="https://github.com/user-attachments/assets/2ed99a74-bffd-40c8-be2f-64eaa51dfc18" />


**Discovered Data Sequences:**

- **s0.bin:** `7f 79 6e 6f 4c 00 03 54 54 53`
- **s1.bin:** `56 51 01 0f 01 55 55 04 0f 02`
- **s2.bin:** `53 05 55 02 03 52 02 01 55 04`
- **s3.bin:** `03 05 01 55 53 56 02 4a 00 00`

Each segment contained exactly 10 bytes of custom structured data right at the baseline padding index (`0x00000000`).

#### Cryptanalysis (Breaking the XOR)

The text representation of `s0.bin` displayed the string `7f796e6f4c`, which maps closely to the reversed string `ynoL` (`Lony`). Recognizing this string configuration pointed directly to a **Bitwise XOR Cipher**.

We reconstructed the segments into a linear physical memory layout sequence (**s0 + s1 + s2 + s3**) yielding the following complete 40-byte hex stream:`7f796e6f4c00035454535651010f015555040f0253055502035202015504030501555356024a0000`

We executed a specialized Python cryptanalysis loop to test all possible single-byte XOR configurations against the linear memory stream:

<img width="952" height="596" alt="image" src="https://github.com/user-attachments/assets/6f836826-46ec-460f-8eab-56169aa8938d" />


#### Script Execution Results:

```
Linear Key 0x37: HNYX{74ccdaf686bb385d2b54e56b3426bda5}77
```

Using the XOR structural key **`0x37`**, the obfuscated data cleanly decrypted into the authentic flag. The decoy file dropped in the file system ended in a `0`, but the real flag safely hidden inside the raw memory fragments terminated properly with a `5`.

#### Final Flag

```
HNYX{74ccdaf686bb385d2b54e56b3426bda5}
```

thats the flag!
