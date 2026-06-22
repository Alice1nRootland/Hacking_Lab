<img width="532" height="396" alt="image" src="https://github.com/user-attachments/assets/d378d9d8-7fb3-4b41-ba67-8a0401f4f6de" />

#### Initial Reconnaissance & Unpacking

Running `file` and basic checks on `vee-em` revealed that it was a 64-bit ELF binary packed with UPX. We unpacked it using the following command:

```bash
upx -d vee-em -o vee-em_unpacked
```

---

#### Analyzing & Patching Anti-Debugging Logic

When running the binary directly, it exited with code `1`. Under `strace` or `gdb`, it also exited immediately.
By disassembling the binary, we identified two main anti-debugging/anti-VM protection routines:

1. **Function at `0x317f`**: Calls `ptrace(PTRACE_TRACEME)`. If this returns `1` (indicating a tracer is already attached), it immediately exits the program. It also attempts to open and parse `/proc/self/status` to check `TracerPid`.
2. **Function at `0x367d`**: Checks for environment variables (`DOCKER_HOST`, `DOCKER_CONTAINER`, `SANDBOXED`, `QEMU_FULL_VERSION`) and files (`/.dockerenv`, `/.dockerinit`) to prevent running under sandboxes or virtualized environments.

To bypass these checks statically, we patched the binary by replacing the first byte of both functions (`0x317f` and `0x367d`) with a `ret` instruction (`0xc3`).

#### Patching Script & Commands

Save the following python code as `patch.py`:

```python
with open("vee-em_unpacked", "rb") as f:
    data = bytearray(f.read())

# Write ret (0xc3) at 0x317f (anti-debug 1)
data[0x317f] = 0xc3

# Write ret (0xc3) at 0x367d (anti-debug 2)
data[0x367d] = 0xc3

with open("vee-em_patched", "wb") as f:
    f.write(data)
```

Then execute the patch and set executable permissions:

```bash
python3 patch.py
chmod +x vee-em_patched
```

---

#### Custom VM Architecture Analysis

The VM operates on a bytecode file named `bin`. The main loop parses sequential VM instructions:

- **Registers**: The VM has four 32-bit registers `R0`, `R1`, `R2`, `R3`.
- **Initialization**: Initially, the registers are populated with the 128-bit MD5 hash of the bytecode file (`bin`).
- **Linear Execution**: The VM executes the bytecode sequentially from start to finish. No branch or jump instructions exist in the bytecode instruction set.
- **Instruction Sizes**:
    - `0x60` (INIT): 1 byte
    - `0x12` (LD_FLAG_LEN): 2 bytes
    - All other instructions: 3 bytes (1 byte opcode, 2 bytes arguments)

#### VM Opcode Table

- `0x10`: `LD_FLAG` (loads a byte from the input flag string)
- `0x11`: `LD_REG` (copies one register to another)
- `0x12`: `LD_FLAG_LEN` (loads flag length into register)
- `0x20`: `ADD_CONST` (register + constant)
- `0x21`: `ADD_REG` (register1 + register2)
- `0x22`: `SUB_CONST` (register - constant)
- `0x30`: `XOR_CONST` (register ^ constant)
- `0x31`: `XOR_REG` (register1 ^ register2)
- `0x40`: `SHL_CONST` (shift left)
- `0x41`: `SHR_CONST` (logical shift right)
- `0x42`: `ROL_CONST` (rotate left)
- `0x43`: `ROR_CONST` (rotate right)
- `0x50`: `ASSERT` (compares register to expected byte, exits with 0 on mismatch)

---

#### Flag Constraint Extraction & SMT Solving

The bytecode initializes `R1` to the flag length and asserts `R1 == 64` (`0x40`), meaning the expected flag length is 64 characters.

The rest of the bytecode acts as an accumulating key-stream verification:

1. An input character is loaded into `R0`.
2. `R0` is XORed with a running accumulator key `R1`.
3. Arithmetic and bitwise rotation operations are applied to `R0`.
4. `R2` copies `R0`, XORs it with `165` (0xa5), and asserts the result against a hardcoded expected byte.
5. The verified result accumulates into `R1` (`ADD_REG R1, R2`) to serve as the key for verifying the next character.

Since all operations are linear and reversible, we translated this bytecode sequence into a SMT solver constraint problem using the Z3 solver in Python.

#### Solver Script & Commands

Save the following python code as `solve.py`:

```python
import z3
import hashlib
import struct

# Load VM bytecode
with open("bin", "rb") as f:
    bytecode = f.read()

# Initialize VM registers to MD5 of the bin file
md5_hash = hashlib.md5(bytecode).digest()
initial_R = list(struct.unpack("<4I", md5_hash))

s = z3.Solver()
flag = [z3.BitVec(f"f_{i}", 8) for i in range(64)]

def to_bv8(val):
    return z3.BitVecVal(val & 0xff, 8) if isinstance(val, int) else val

R = [to_bv8(x) for x in initial_R]

def z3_rol(val, n):
    n = n & 7
    return val if n == 0 else (val << n) | z3.LShR(val, 8 - n)

def z3_ror(val, n):
    n = n & 7
    return val if n == 0 else z3.LShR(val, n) | (val << (8 - n))

pc = 0
while pc < len(bytecode):
    opcode = bytecode[pc]
    pc += 1

    if opcode == 0x60:
        continue
    elif opcode == 0x12:
        reg = bytecode[pc] & 3
        pc += 1
        R[reg] = to_bv8(64)
    else:
        if pc + 1 >= len(bytecode): break
        arg1 = bytecode[pc]
        arg2 = bytecode[pc+1]
        pc += 2

        reg1 = arg1 & 3
        reg2 = arg2 & 3

        if opcode == 0x10:
            R[reg1] = flag[arg2]
        elif opcode == 0x11:
            R[reg1] = R[reg2]
        elif opcode == 0x20:
            R[reg1] = R[reg1] + to_bv8(arg2)
        elif opcode == 0x21:
            R[reg1] = R[reg1] + R[reg2]
        elif opcode == 0x22:
            R[reg1] = R[reg1] - to_bv8(arg2)
        elif opcode == 0x30:
            R[reg1] = R[reg1] ^ to_bv8(arg2)
        elif opcode == 0x31:
            R[reg1] = R[reg1] ^ R[reg2]
        elif opcode == 0x40:
            R[reg1] = R[reg1] << to_bv8(arg2)
        elif opcode == 0x41:
            R[reg1] = z3.LShR(R[reg1], to_bv8(arg2))
        elif opcode == 0x42:
            R[reg1] = z3_rol(R[reg1], arg2)
        elif opcode == 0x43:
            R[reg1] = z3_ror(R[reg1], arg2)
        elif opcode == 0x50:
            s.add(R[reg1] == to_bv8(arg2))

if s.check() == z3.sat:
    m = s.model()
    sol = bytearray(m[flag[i]].as_long() for i in range(64))
    print("Found flag input:", sol.decode())
```

Execute the solver:

```bash
python3 solve.py
```

This successfully outputs the 64-character input string:
`h4h4_5YmB0l1c_eX3cuT10n_g0_brrr_467f21b28c37e11efbb0d5ac2e642582`

---

#### Flag Retrieval

Execute the patched binary with the solved input:

```bash
./vee-em_patched h4h4_5YmB0l1c_eX3cuT10n_g0_brrr_467f21b28c37e11efbb0d5ac2e642582
```

It prints the final flag:
`HNYX{93aa9232c8b2fbd1d4d15dbafa0d163c}`
