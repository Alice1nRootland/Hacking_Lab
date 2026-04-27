# 🚩 UMCS 2026 CTF Write-ups

<img width="1280" height="710" alt="image" src="https://github.com/user-attachments/assets/24b24a4e-fbd5-42a7-a015-c5a7b95bacf6" />



**📄 [View the Full Team Write-up Report Here](https://remarkable-xenon-ff5.notion.site/UMCS-2026-CTF-Write-up-Report-34ea6f58415f80388995d857d9a7cbb3)**

## 🛡️ Team Brief: ByteBandits
We competed in the UMCS 2026 CTF as team **ByteBandits**.
* **Institution:** Universiti Teknikal Malaysia Melaka (UTeM)
* **Final Ranking:** 17th / 190 Teams
* **Total Score:** 2150 Points
* **Event Duration:** 24 Hours
* **Team Members:** Alice1nR00TI@nd (Captain), ijat70, jasonpeh83, choomq, and myself.

## 💻 My Challenge Solves

### Reverse Engineering

* **Donut Calculator:**
  The challenge provided a Donut Loader wrapping a binary. I used `donut-decryptor` to extract the underlying PE file from offset `0x2625`. Using Binary Ninja, I identified two decryption loops in the `nice()` function utilizing keys `nPcSecret` and `PcFlag`. The first stage involved XOR-decrypting a data section with the 9-byte `nPcSecret` key, revealing a PowerShell command containing the first half of the flag. For the second stage, I replicated a modular inverse key rotation in CyberChef to decrypt a 24-byte buffer with the `nPcFlag` key to extract the remaining shellcode and flag.

* **Horus:**
  I analyzed a native x64 PE32+ executable and bypassed `IsDebuggerPresent` checks. After identifying a 64-bit constant key (`0x4145013510415222`) used in an RC4 cipher, I wrote a Python script to statically decrypt the payload. The resulting `.NET` Assembly contained a class `CliLoader` with a secondary RC4 encryption function named `entahlahnak`. I applied the hex representation of the stage 1 key to decrypt the `cipherHex` string and retrieve the final flag.

### Forensics

* **The Winning Shot:**
  Analyzing the unstripped `winning_shot` executable and core dump with GDB, I noticed the program wiped the memory tables before dumping. I investigated `movabs` instructions in the `main` function's disassembly that moved 64-bit hex values directly into the stack. By extracting these Little-Endian hex strings, reversing their byte order, and converting them to ASCII, I reconstructed the hidden flag fragments.

* **Dojo Routing Breach:**
  Initial PCAP analysis showed a massive UDP flood (encoded with Shikata Ga Nai) acting as a decoy. I filtered for OSPF traffic and isolated the `ospf.advrouter` Advertising Router IDs. By treating the Source IP as the index and the Router ID as the data, I sorted the packets by Source IP to piece together the hidden exfiltration payload.

### Crypto & Misc

* **Phantom Anthem of DTC (Crypto):**
  This challenge required applying phase inversion on a stereo WAV file (`DTC_Midnight.wav`). By subtracting the right channel from the left, I canceled out the identical "Anthem" audio to reveal a hidden "Phantom" signal containing Morse code. After decoding the Morse code to `LUYKBBFZEJNHPKEXGNTOTHIUYCO`,
