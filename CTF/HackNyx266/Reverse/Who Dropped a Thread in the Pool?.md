<img width="582" height="837" alt="image" src="https://github.com/user-attachments/assets/bdc342e3-3344-45b7-86e1-2e51a8c32478" />

#### Binary Reconnaissance

First, we inspected the target file to determine its file type and basic properties:

```bash
file PoolParty.exe
```

This confirmed it is a PE32+ (64-bit) console executable, stripped, and compiled with MinGW.

---

#### Resource Extraction

The binary contains three embedded resources:

- `res_3_1.bin` (Type 3, ID 1)
- `res_10_1.bin` (Type 10, ID 1)
- `res_14_pool.bin` (Type 14, ID 1)

We extracted the resource data using a Python script leveraging `pefile`:

```python
# dump_res.py
import pefile

pe = pefile.PE("PoolParty.exe")
for rsrc in pe.DIRECTORY_ENTRY_RESOURCE.entries:
    for entry in rsrc.directory.entries:
        if hasattr(entry, "directory"):
            for subentry in entry.directory.entries:
                if hasattr(subentry, "data"):
                    data_rva = subentry.data.struct.OffsetToData
                    size = subentry.data.struct.Size
                    data = pe.get_data(data_rva, size)
                    filename = f"res_{rsrc.id}_{entry.id}.bin"
                    with open(filename, "wb") as f:
                        f.write(data)
```

Execution command:

```bash
python3 dump_res.py
```

---

#### Decompilation and Static Analysis

Using Ghidra headless analyzer, we decompiled the key functions:

```bash
/usr/share/ghidra/support/analyzeHeadless /tmp tempProj -import PoolParty.exe -scriptPath . -postScript decomp.py -overwrite > decomp_output.txt 2>&1
```

From this decompilation, we mapped the program flow:

1. **Mutex Check:** The application checks for the mutex `PoolPartyGatekeeper` to prevent multiple concurrent instances.
2. **Resource Loading:** It reads resource `10/1` (64 bytes) and decrypts it dynamically into 8 separate 8-byte blocks allocated on the heap (stored in pointers `DAT_14000a100` through `DAT_14000a140`).
3. **Server Initialization:** It binds a TCP socket to port `59172` and starts listening for connections.
4. **Thread Pool / Callback Dispatch:** When client data is received, the network callback uses `WSARecv` to read a 5-byte packet. The first byte acts as the lane index (0 to 7) and the remaining 4 bytes contain a validation value.
5. **Thread Execution (`FUN_1400017c0`):** The thread pool callback decrypts one of the 8 heap blocks in memory, applies a custom XOR transformation to turn it into executable instructions, executes it, and registers its output.
6. **Watchdog and Lifeguards:**
    - **Lifeguards:** Active checks for debuggers (`IsDebuggerPresent`, `CheckRemoteDebuggerPresent`, `NtQueryInformationProcess`).
    - **Watchdog:** A 3-second `GetTickCount64` threshold within the execution block prevents debugging. A separate watchdog thread deletes files and terminates after 60 seconds.

---

#### Reverse Engineering the Decryption & Invariants

Each of the 8 decrypted blocks represents a small 8-byte shellcode block that returns a `uint` value:

```nasm
mov eax, imm32
ret
nop
nop
```

This is represented in machine code as:

- `T1 = [0xb8, imm_b0, imm_b1, imm_b2]`
- `T2 = [imm_b3, 0xc3, 0x90, 0x90]`

The decryption routine modifies the raw heap bytes `H1` and `H2` using:

$$
T_1 = H_1 \oplus K
$$

$$
T_2 = H_2 \oplus K
$$

Where $K$ is a 4-byte key. Since $K$ is applied to both halves:

$$
T_1 \oplus T_2 = H_1 \oplus H_2
$$

Using this mathematical relation, we extracted the individual byte outputs of the shellcode blocks:

```python
# Solved imm32 values
imm32 = [
    0xa7e6b1b7, # Lane 0
    0xb38e8c84, # Lane 1
    0x88e086b3, # Lane 2
    0xccd48dcf, # Lane 3
    0xaddba08d, # Lane 4
    0x9ee08f90, # Lane 5
    0x9acd97ab, # Lane 6
    0xffc29b9e  # Lane 7
]
```

---

#### Flag Reconstruction

The scoreboard reorders and outputs the values as:

\text{output}[\text{lane}] = (\text{ImageBase\_Key} \oplus imm32[\text{lane}])

Since the flag starts with `"HNYX"`, the first block must decode to `"HNYX"` (little endian: `0x58594e48`). Aligning the first block with lane 1 yielded the global XOR key `0xffffffff`.

Executing the final decryption script:

```python
imm32 = [
    0xa7e6b1b7, 0xb38e8c84, 0x88e086b3, 0xccd48dcf,
    0xaddba08d, 0x9ee08f90, 0x9acd97ab, 0xffc29b9e
]
K = 0xffffffff

blocks = [((K ^ imm ^ 0x400000).to_bytes(4, "little")) for imm in imm32]
flag = blocks[0] + blocks[1] + blocks[2] + blocks[3] + blocks[4] + blocks[5] + blocks[6] + blocks[7]
print(flag.decode().rstrip("\x00"))
```

flag:

**`HNYX{s1LLy_w0rk3r_dRop_aThread}`**
