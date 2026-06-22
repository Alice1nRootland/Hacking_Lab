<img width="590" height="472" alt="image" src="https://github.com/user-attachments/assets/6fbce31f-9792-42d5-ad29-b714c8f3702b" />

#### Initial Analysis

Let's inspect the file type and check for any plain strings using file and strings:

<img width="1087" height="90" alt="image" src="https://github.com/user-attachments/assets/3dd449b5-7ec8-494e-9ca9-256f16964618" />


<img width="452" height="212" alt="image" src="https://github.com/user-attachments/assets/43a6ba0e-bb20-447a-a50b-08329be75622" />


Executing the program under `ltrace` with a test input reveals basic behavior:

<img width="797" height="281" alt="image" src="https://github.com/user-attachments/assets/99b3cfc3-3a75-4d2e-8f27-f000b61ca9f2" />


---

#### Disassembly Analysis

Disassembling the `.text` section using `gdb` shows the input validation logic inside the `main` function (located starting at `0x1209`):

### Input Splitting

The program reads up to 64 bytes of input. It verifies that the input (excluding the newline) is exactly **16 characters** long:

```
   0x0000000000001292:	cmp    $0x10,%rdx
   0x0000000000001296:	je     0x12ce
```

If the length is 16, it splits the input into two 8-byte blocks:

- `x` (First 8 bytes) stored at `rsp + 0x77`
- `y` (Second 8 bytes) stored at `rsp + 0x6e`

```
   0x00000000000012ce:	lea    0x80(%rsp),%rsi        # input[0..7]
   0x00000000000012d6:	lea    0x77(%rsp),%rdi        # x
   0x00000000000012db:	mov    $0x8,%edx
   0x00000000000012e0:	call   0x10b0 <strncpy@plt>
   ...
   0x00000000000012ea:	lea    0x88(%rsp),%rsi        # input[8..15]
   0x00000000000012f2:	lea    0x6e(%rsp),%rdi        # y
   0x00000000000012f7:	mov    $0x8,%edx
   0x00000000000012fc:	call   0x10b0 <strncpy@plt>
```

---

#### Constraints on Part 1 (`x = input[0..7]`)

The binary verifies the first 8 characters against a system of equations:

1. **`x[0] + x[4] == 198`** (0xc6)
2. **`x[1] * x[6] == 10605`** (0x296d)
3. **`x[2] - x[3] == 17`** (0x11)
4. **`x[5] + x[7] == 204`** (0xcc)
5. **`x[2] * x[0] == 12154`** (0x2f7a)
6. **`x[1] + x[5] == 214`** (0xd6)
7. **`x[1] - x[3] == 4`** (from `x[3] - x[1] == -4`)
8. **`x[4] * x[7] == 9025`** (0x2341)

Solving this system yields:

- `x[0] = 103` (`g`)
- `x[1] = 105` (`i`)
- `x[2] = 118` (`v`)
- `x[3] = 101` (`e`)
- `x[4] = 95` (`_`)
- `x[5] = 109` (`m`)
- `x[6] = 101` (`e`)
- `x[7] = 95` (`_`)

Which gives `x = "give_me_"`.

---

#### Constraints on Part 2 (`y = input[8..15]`)

The binary verifies the next 8 characters using an XOR chain checked in reverse, starting with a hardcoded constant:

1. **`y[7] == 0x67`** (`g`)
2. **`y[6] ^ y[7] == 0x6`**
3. **`y[5] ^ y[6] == 0xd`**
4. **`y[4] ^ y[5] == 0xa`**
5. **`y[3] ^ y[4] == 0x39`**
6. **`y[2] ^ y[3] == 0x3a`**
7. **`y[1] ^ y[2] == 0xd`**
8. **`y[0] ^ y[1] == 0x1c`**
9. **`y[0] ^ y[7] == 0x13`** (used as a cross-verification)

Solving the XOR chain:

- `y[7] = 0x67` (`g`)
- `y[6] = 0x67 ^ 0x06 = 0x61` (`a`)
- `y[5] = 0x61 ^ 0x0d = 0x6c` (`l`)
- `y[4] = 0x6c ^ 0x0a = 0x66` (`f`)
- `y[3] = 0x66 ^ 0x39 = 0x5f` (`_`)
- `y[2] = 0x5f ^ 0x3a = 0x65` (`e`)
- `y[1] = 0x65 ^ 0x0d = 0x68` (`h`)
- `y[0] = 0x68 ^ 0x1c = 0x74` (`t`)

Verify cross-verification: `y[0] ^ y[7] = 0x74 ^ 0x67 = 0x13`. Correct.

Which gives `y = "the_flag"`.

---

#### Flag Generation Logic

If both blocks are correct, the binary sums up the ASCII values of the input characters:

$$
\text{seed} = \sum_{i=0}^{15} \text{input}[i] = 1667
$$

It then seeds the random number generator:

```c
srand(1667);
```

An encrypted array of 32 bytes (stored as four 64-bit integers on stack: `0x8c3d7258a6424eb7`, `0xd4e6a2be56211077`, `0x0d22d5576960e18a`, `0x90259546b2cd94f3`) is XORed byte-by-byte with the output of `rand()`:

```c
for (int i = 0; i < 32; i++) {
    flag[i] = encrypted[i] ^ rand();
}
```

---

#### Solve Script

Here is a Python script that replicates the decryption logic:

```python
import ctypes

# Load standard C library to match the glibc rand() output
libc = ctypes.CDLL("libc.so.6")

# Set the seed derived from sum(b"give_me_the_flag")
seed = sum(b"give_me_the_flag")
libc.srand(seed)

# 32-byte encrypted ciphertext loaded from the stack (little endian representation)
ciphertext = (
    (0x8c3d7258a6424eb7).to_bytes(8, 'little') +
    (0xd4e6a2be56211077).to_bytes(8, 'little') +
    (0x0d22d5576960e18a).to_bytes(8, 'little') +
    (0x90259546b2cd94f3).to_bytes(8, 'little')
)

flag = bytearray()
for b in ciphertext:
    # Emulate byte xor with next rand() call
    flag.append(b ^ (libc.rand() & 0xff))

print(f"Flag: HNYX{{{flag.decode('ascii')}}}")
```

---

#### Execution and Flag

Running the binary with the secret:
<img width="595" height="286" alt="image" src="https://github.com/user-attachments/assets/f87ffa18-756e-446c-99bc-0777804b30a8" />


**Flag**: `HNYX{771cd10bc38e5c6141fef689daf5a0b7}`
