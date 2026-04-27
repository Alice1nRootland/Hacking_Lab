<img width="617" height="660" alt="image" src="https://github.com/user-attachments/assets/588e8bae-1d9c-429b-ac9d-b752e616a76c" />

## Initial Triage & Unpacking

The challenge provided a file named `calculator.exe`. Preliminary analysis suggested it was a **Donut Loader**—a common tool used by attackers to wrap shellcode or other executables into a position-independent blob

### Extracting the Module

I used the `donut-decryptor` tool to peel back the first layer of obfuscation. The tool successfully identified a Donut instance at `0x2e25` and extracted the underlying PE file.

<img width="1223" height="350" alt="image" src="https://github.com/user-attachments/assets/892cc18c-c295-43e0-a090-2bbbf9539887" />

**Result:** Generated `mod_calculator.exe`

### Static Analysis (Binary Ninja)

Despite unpacking the Donut wrapper, a `strings` search on `mod_calculator.exe` yielded no flag. This indicated that the flag was further encrypted within the binary's data sections.

### Identifying the Decryption Engine

I loaded the unpacked module into **Binary Ninja** and analyzed the `nice()` function. I discovered two distinct decryption loops using different keys stored in the `.rdata` section.

- **Key 1:** `nPcSeCreT` (9 bytes)
- **Key 2:** `nPcF1aG` (7 bytes)

<img width="1357" height="654" alt="image" src="https://github.com/user-attachments/assets/b0a20ddd-8416-420c-8c56-2dc603b93602" />

### Decrypting Stage 1: The PowerShell Pivot

The first loop XORs data from the `_.data` section (`0x140003000`) with the 9-byte key `nPcSeCreT`.

<img width="1193" height="428" alt="image" src="https://github.com/user-attachments/assets/d0410327-b71d-4162-855b-88b496a85bf5" />

### Decryption in CyberChef

I extracted the hex from `0x140003000` and performed the XOR operation. This revealed a hidden, fileless PowerShell command.

<img width="1536" height="496" alt="image" src="https://github.com/user-attachments/assets/0408aa4d-fc77-4e98-8759-529e005c4075" />

<img width="1537" height="437" alt="image" src="https://github.com/user-attachments/assets/80919755-c5c3-4052-ab9d-942c728cd863" />

Decrypted Payload:
The command contained a long -EncodedCommand. After decoding the Base64 (UTF-16LE), I found Flag Part 1

```sql
$flag_part1 = 'UMCS{Ap1_HaSH1n5_Pr0c3ss_Ha';
```

### Decrypting Stage 2: The Binary Buffer

The second loop at `0x1400015ba` used a 7-byte rotating XOR key (`nPcF1aG`) to decrypt a 24-byte buffer at the `bad` label (`0x140003590`).

<img width="1201" height="76" alt="image" src="https://github.com/user-attachments/assets/8e12ead9-cbd5-4779-b766-a573a1fc1644" />

### The Modulo Logic

The assembly utilized a modular inverse (`imul rax, 0x24924925`) to handle the key rotation. I replicated this logic in CyberChef.

<img width="1168" height="482" alt="image" src="https://github.com/user-attachments/assets/17ffaae6-2386-40bf-9390-6c2c46b985e7" />

**Decrypted Part 2:**

```
11owInG_D0nuT_sHellcode}
```

**Flag:** `UMCS{Ap1_HaSH1n5_Pr0c3ss_Ha11owInG_D0nuT_sHellcode}`
