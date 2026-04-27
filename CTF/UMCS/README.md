# 🚩 UMCS 2026 CTF Write-ups

<img width="1280" height="710" alt="image" src="https://github.com/user-attachments/assets/24b24a4e-fbd5-42a7-a015-c5a7b95bacf6" />


## 🛡️ Team Brief: ByteBandits
We competed in the UMCS 2026 CTF as team **ByteBandits**.
* [cite_start]**Institution:** Universiti Teknikal Malaysia Melaka (UTeM) [cite: 4430]
* [cite_start]**Final Ranking:** 17th / 190 Teams [cite: 4430]
* [cite_start]**Total Score:** 2150 Points [cite: 4430]
* [cite_start]**Event Duration:** 24 Hours [cite: 4430]
* [cite_start]**Team Members:** Alice1nR00TI@nd (Captain), ijat70, jasonpeh83, choomq, and myself[cite: 4430].

## 💻 My Challenge Solves

### Reverse Engineering

* **Donut Calculator:**
  [cite_start]The challenge provided a Donut Loader wrapping a binary[cite: 4507]. [cite_start]I used `donut-decryptor` to extract the underlying PE file from offset `0x2625`[cite: 4508]. [cite_start]Using Binary Ninja, I identified two decryption loops in the `nice()` function utilizing keys `nPcSecret` and `PcFlag`[cite: 4512, 4513]. [cite_start]The first stage involved XOR-decrypting a data section with the 9-byte `nPcSecret` key, revealing a PowerShell command containing the first half of the flag[cite: 4514, 4521]. [cite_start]For the second stage, I replicated a modular inverse key rotation in CyberChef to decrypt a 24-byte buffer with the `nPcFlag` key to extract the remaining shellcode and flag[cite: 4522, 4523].

* **Horus:**
  [cite_start]I analyzed a native x64 PE32+ executable and bypassed `IsDebuggerPresent` checks[cite: 4524, 4528]. [cite_start]After identifying a 64-bit constant key (`0x4145013510415222`) used in an RC4 cipher, I wrote a Python script to statically decrypt the payload[cite: 4533, 4534, 4536]. [cite_start]The resulting `.NET` Assembly contained a class `CliLoader` with a secondary RC4 encryption function named `entahlahnak`[cite: 4539, 4541]. [cite_start]I applied the hex representation of the stage 1 key to decrypt the `cipherHex` string and retrieve the final flag[cite: 4550, 4551].

### Forensics

* **The Winning Shot:**
  [cite_start]Analyzing the unstripped `winning_shot` executable and core dump with GDB, I noticed the program wiped the memory tables before dumping[cite: 4595, 4604]. I investigated `movabs` instructions in the `main` function's disassembly that moved 64-bit hex values directly into the stack[cite: 4602, 4603]. [cite_start]By extracting these Little-Endian hex strings, reversing their byte order, and converting them to ASCII, I reconstructed the hidden flag fragments[cite: 4610, 4611].

* **Dojo Routing Breach:**
  [cite_start]Initial PCAP analysis showed a massive UDP flood (encoded with Shikata Ga Nai) acting as a decoy[cite: 4617, 4618]. [cite_start]I filtered for OSPF traffic and isolated the `ospf.advrouter` Advertising Router IDs[cite: 4619, 4620]. [cite_start]By treating the Source IP as the index and the Router ID as the data, I sorted the packets by Source IP to piece together the hidden exfiltration payload[cite: 4622, 4623].

### Crypto & Misc

* **Phantom Anthem of DTC (Crypto):**
  [cite_start]This challenge required applying phase inversion on a stereo WAV file (`DTC_Midnight.wav`)[cite: 4675, 4676]. By subtracting the right channel from the left, I canceled out the identical "Anthem" audio to reveal a hidden "Phantom" signal containing Morse code[cite: 4675, 4676]. After decoding the Morse code to `LUYKBBFZEJNHPKEXGNTOTHIUYCO`, I used a Vigenère cipher with the key `TUNKU` (derived from the university's first chancellor) to decrypt the string and extract the flag words[cite: 4679, 4681].

* **Noisy_Penguins (Misc):**
  [cite_start]Using `mkvinfo`, I discovered a 46MB `PINGU.mp4` attachment hidden inside a Matroska (`.mkv`) container[cite: 4649, 4651]. [cite_start]I extracted the attachment with `ffmpeg` and found a `tx3g` subtitle track[cite: 4651, 4655]. [cite_start]Extracting the subtitles to `.srt` format revealed Base64 encoded strings mapped to specific video timestamps[cite: 4655, 4658]. [cite_start]Decoding the concatenated Base64 strings yielded the flag[cite: 4659].
