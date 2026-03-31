i pass the exe file in https://dogbolt.org/?id=de8ae317-9e7b-4547-8595-af6d1206e11c#angr=2612&Hex-Rays=1777&Ghidra=2641&BinaryNinja=1813

<img width="1276" height="686" alt="image" src="https://github.com/user-attachments/assets/badbe7e6-cd7b-4038-ab35-fc16dd17b005" />

then i copy the whole ghidra 
and paste it to gemini and here the response

Ayy, look what we got here—some sweet, sweet decompiled code. This smells like a classic **CrackMe** challenge, or at least a simple local access control check. It's a quick hit for a reverse engineer.

The core logic is right inside the `main` function. Here's the breakdown, hacker-style.

---

## The Exploit Vector: How to Bypass the Check

The goal is to hit the `if ((char)uVar1 == '\x01')` branch in `main` to get the "good stuff" (the decrypted message).

The check is here:

C

  `uVar1 = iequals(local_68,local_48);
  if ((char)uVar1 == '\x01') {
    ... // ACCESS GRANTED PATH
  }
  else {
    ... // ACCESS DENIED PATH
  }`

1. **`local_48` (The Secret):** This string is populated by the function `getHostname_abi_cxx11_(local_48)`.
    - If you peek at `getHostname_abi_cxx11_`, it calls the Windows API function **`GetComputerNameA`**.
    - **The secret is the current machine's network name (hostname).**
2. **`local_68` (Your Input):** This string captures your input after the prompt: `std::operator<<((ostream *)&_ZSt4cout,"What\'s your name: ");`
3. **The Check (`iequals`):** The program then calls `iequals(local_68, local_48)`.
    - Looking at the `iequals` function, it checks if the two strings (`param_1` and `param_2`) are the same **length** and then uses a custom lambda function that calls **`tolower`** on each character pair.
    - **The check is a case-insensitive string comparison against the computer's hostname.**

### The Key to Access

To get access, you simply need to provide the **hostname** of the machine running this executable when it asks for your name. The capitalization doesn't matter.

> TL;DR: The input you need to provide is the Case-Insensitive Computer Name (Hostname) of the system running the executable.
> 

---

##  Decoding the Flag (The "Good Stuff")

Once the check passes, it enters the success block. The code encrypts a message using a simple **XOR cipher**.

### The Cipher Parameters

- **Encrypted Data:** A 41-byte array named `local_98`.
- **Key:** A single byte, `local_21 = 0x67`. This is the XOR key.
- **Decryption Loop:**C
    
    `for (local_20 = local_98; *local_20 != 0; local_20 = local_20 + 1) {
      std::operator<<((ostream *)&_ZSt4cout,*local_20 ^ 0x67);
    }`
    
    The loop iterates over the `local_98` byte array until it hits a null terminator (`*local_20 != 0`). It takes each byte, XORs it with the key (`0x67`), and prints the resulting character.
    

### The Ciphertext

Here are the hexadecimal values of `local_98`:

| **Index** | **Value (Hex)** |
| --- | --- |
| 0x00 | 0xE |
| 0x01 | 0x0 |
| 0x02 | 0x8 |
| 0x03 | 0xF |
| 0x04 | 0x55 |
| 0x05 | 0x52 |
| 0x06 | 0x1C |
| 0x07 | 0x4 |
| 0x08 | 0x6 |
| 0x09 | 0x52 |
| 0x0A | 0x3 |
| 0x0B | 0x6 |
| 0x0C | 0x55 |
| 0x0D | 0x2 |
| 0x0E | 0x51 |
| 0x0F | 0x55 |
| 0x10 | 0x2 |
| 0x11 | 0x53 |
| 0x12 | 0x5E |
| 0x13 | 0x3 |
| 0x14 | 0x4 |
| 0x15 | 0x53 |
| 0x16 | 0x2 |
| 0x17 | 0x6 |
| 0x18 | 0x5E |
| 0x19 | 0x2 |
| 0x1A | 0x55 |
| 0x1B | 0x2 |
| 0x1C | 0x6 |
| 0x1D | 0x55 |
| 0x1E | 0x50 |
| 0x1F | 0x3 |
| 0x20 | 0x52 |
| 0x21 | 0x52 |
| 0x22 | 0x51 |
| 0x23 | 0x2 |
| 0x24 | 0x50 |
| 0x25 | 0x2 |
| 0x26 | 0x4 |
| 0x27 | 0x1A |
| 0x28 | 0x0 |

### Decryption

To decrypt it, we simply apply the XOR operation: **$C \oplus K = P$**, where $C$ is the ciphertext byte, $K$ is the key ($0x67$), and $P$ is the plaintext character.

| **Ciphertext (Hex)** | **Key (Hex)** | **Plaintext (Hex)** | **Plaintext (ASCII)** |
| --- | --- | --- | --- |
| 0xE | 0x67 | 0x67 $\oplus$ 0xE = 0x71 | **q** |
| 0x0 | 0x67 | 0x67 $\oplus$ 0x0 = 0x67 | **g** |
| 0x8 | 0x67 | 0x67 $\oplus$ 0x8 = 0x6F | **o** |
| 0xF | 0x67 | 0x67 $\oplus$ 0xF = 0x68 | **h** |
| 0x55 | 0x67 | 0x67 $\oplus$ 0x55 = 0x32 | **2** |
| 0x52 | 0x67 | 0x67 $\oplus$ 0x52 = 0x35 | **5** |
| 0x1C | 0x67 | 0x67 $\oplus$ 0x1C = 0x7B | **{** |
| 0x4 | 0x67 | 0x67 $\oplus$ 0x4 = 0x63 | **c** |
| 0x6 | 0x67 | 0x67 $\oplus$ 0x6 = 0x61 | **a** |
| 0x52 | 0x67 | 0x67 $\oplus$ 0x52 = 0x35 | **5** |
| 0x3 | 0x67 | 0x67 $\oplus$ 0x3 = 0x64 | **d** |
| 0x6 | 0x67 | 0x67 $\oplus$ 0x6 = 0x61 | **a** |
| 0x55 | 0x67 | 0x67 $\oplus$ 0x55 = 0x32 | **2** |
| 0x2 | 0x67 | 0x67 $\oplus$ 0x2 = 0x65 | **e** |
| 0x51 | 0x67 | 0x67 $\oplus$ 0x51 = 0x36 | **6** |
| 0x55 | 0x67 | 0x67 $\oplus$ 0x55 = 0x32 | **2** |
| 0x2 | 0x67 | 0x67 $\oplus$ 0x2 = 0x65 | **e** |
| 0x53 | 0x67 | 0x67 $\oplus$ 0x53 = 0x34 | **4** |
| 0x5E | 0x67 | 0x67 $\oplus$ 0x5E = 0x39 | **9** |
| 0x3 | 0x67 | 0x67 $\oplus$ 0x3 = 0x64 | **d** |
| 0x4 | 0x67 | 0x67 $\oplus$ 0x4 = 0x63 | **c** |
| 0x53 | 0x67 | 0x67 $\oplus$ 0x53 = 0x34 | **4** |
| 0x2 | 0x67 | 0x67 $\oplus$ 0x2 = 0x65 | **e** |
| 0x6 | 0x67 | 0x67 $\oplus$ 0x6 = 0x61 | **a** |
| 0x5E | 0x67 | 0x67 $\oplus$ 0x5E = 0x39 | **9** |
| 0x2 | 0x67 | 0x67 $\oplus$ 0x2 = 0x65 | **e** |
| 0x55 | 0x67 | 0x67 $\oplus$ 0x55 = 0x32 | **2** |
| 0x2 | 0x67 | 0x67 $\oplus$ 0x2 = 0x65 | **e** |
| 0x6 | 0x67 | 0x67 $\oplus$ 0x6 = 0x61 | **a** |
| 0x55 | 0x67 | 0x67 $\oplus$ 0x55 = 0x32 | **2** |
| 0x50 | 0x67 | 0x67 $\oplus$ 0x50 = 0x37 | **7** |
| 0x3 | 0x67 | 0x67 $\oplus$ 0x3 = 0x64 | **d** |
| 0x52 | 0x67 | 0x67 $\oplus$ 0x52 = 0x35 | **5** |
| 0x52 | 0x67 | 0x67 $\oplus$ 0x52 = 0x35 | **5** |
| 0x51 | 0x67 | 0x67 $\oplus$ 0x51 = 0x36 | **6** |
| 0x2 | 0x67 | 0x67 $\oplus$ 0x2 = 0x65 | **e** |
| 0x50 | 0x67 | 0x67 $\oplus$ 0x50 = 0x37 | **7** |
| 0x2 | 0x67 | 0x67 $\oplus$ 0x2 = 0x65 | **e** |
| 0x4 | 0x67 | 0x67 $\oplus$ 0x4 = 0x63 | **c** |
| 0x1A | 0x67 | 0x67 $\oplus$ 0x1A = 0x7D | **}** |

### The Flag

The resulting flag is:

qgoh25{ca5da2e62e49dc4ea9e2ea27d556e7ec}

---

Got a deeper reversing challenge you're wrestling with? This was just a warm-up. Let's dig into some real exploit theory next, if you're up for it.

<img width="858" height="192" alt="image" src="https://github.com/user-attachments/assets/60accc6c-0caa-41ee-b533-810bc921a461" />

the i just change to

`igoh25{ca5da2e62e49dc4ea9e2ea27d556e7ec}`
