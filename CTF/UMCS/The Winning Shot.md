<img width="607" height="700" alt="image" src="https://github.com/user-attachments/assets/1993c351-3334-4cfd-9ef1-74acfc73f796" />

#### 1. Initial Reconnaissance

We are provided with a zip file containing three items: `winning_shot` (an ELF executable), `core.170390` (a core dump), and `pool` (an image).

<img width="1070" height="94" alt="image" src="https://github.com/user-attachments/assets/a5126f9a-1751-43ca-99d3-73c25c8e3734" />

The file `pool` is a JPEG showing a **black 8-ball**, a hint that the "winning shot" or the core of the challenge involves the number 8 or the 8th ball.

### Disassembling the Binary

Since the binary was **not stripped**, we could use **GDB (GNU Debugger)** to look at the source logic of the `main` function to see how it handled the flag.

<img width="777" height="785" alt="image" src="https://github.com/user-attachments/assets/33987cd2-786b-4600-bf3e-3729d40e3dc7" />

Within the disassembly, we observed a series of **`movabs`** instructions. These instructions were moving 64-bit (8-byte) hexadecimal values directly into the stack. Because the program "wiped the table" (cleared memory) before the core dump was generated, the flag wasn't in the memory buffers, but it remained visible in the **code instructions** themselves.

<img width="1074" height="724" alt="image" src="https://github.com/user-attachments/assets/67dc8d86-a67f-4c81-9b1b-cc4e0cebf69a" />

<img width="831" height="730" alt="image" src="https://github.com/user-attachments/assets/286cc108-4d06-456c-9a0b-d6cbe0a20518" />

<img width="787" height="727" alt="image" src="https://github.com/user-attachments/assets/f5ac26ed-f740-4282-9868-8dfa2d834b02" />

<img width="775" height="358" alt="image" src="https://github.com/user-attachments/assets/9330780f-c731-45ac-8863-df47a33a7cf4" />

## Reconstructing the Flag

The hex values were stored in **Little-Endian** format, meaning the bytes are stored in reverse order. To find the flag, we convert each hex value to ASCII and read them sequentially.

| **GDB Instruction (Hex)** | **Little-Endian Bytes** | **ASCII Fragment** |
| --- | --- | --- |
| `0x6e316b7b53434d55` | `55 43 4d 53 7b 6b 31 6e` | `UMCS{k1n` |
| `0x336e335f63317433` | `33 74 31 63 5f 33 6e 33` | `3t1c_3n3` |
| `0x306333725f796772` | `72 67 79 5f 72 33 63 30` | `rgy_r3c0` |
| `0x72665f6433723376` | `76 33 72 33 64 5f 66 72` | `v3r3d_fr` |
| `0x7230635f6d307266` | `66 72 30 6d 5f 63 30 72` | `fr0m_c0r` |
| `0x7d706d75645f33` | `33 5f 64 75 6d 70 7d` | `3_dump}` |

**Flag:** `UMCS{k1n3t1c_3n3rgy_r3c0v3r3d_fr0m_c0r3_dump}`
