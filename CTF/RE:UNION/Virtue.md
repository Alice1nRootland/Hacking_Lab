<img width="492" height="469" alt="image" src="https://github.com/user-attachments/assets/f59ad5f4-5b5e-4f0e-ab47-f7d28b1eec16" />

## 1. Initial Analysis

We started with two files: an executable `a.out` and a data file `virtue`.

Running the `file` command revealed that `a.out` is an unstripped 64-bit ELF binary, and `virtue` is raw data.

<img width="1594" height="195" alt="image" src="https://github.com/user-attachments/assets/926e40b3-71c1-419b-8d0d-edf3fdbd3b8b" />

Trying to run `a.out` directly resulted in no output. Analyzing the `main` function in Ghidra (or via `objdump`) revealed that the program expects a filename as an argument.

Bash

`$ ./a.out virtue
Enter flag:`

This confirmed that `a.out` is likely a **Virtual Machine (VM)** and `virtue` is the **bytecode** it executes.

## 2. Reverse Engineering the VM (`a.out`)

Since the binary was not stripped, we could easily locate the `run` function (address `0x11d9`), which contained the main interpretation loop.

By mapping the switch cases in the `run` function to their operations, we reconstructed the instruction set architecture (ISA) of the VM.

### VM Architecture

- **Registers:** An array of 256 bytes (located at `regs`).
- **Zero Flag (ZF):** A boolean flag set by comparison instructions.
- **Instruction Pointer (PC):** Points to the current byte in the `virtue` file.

<img width="345" height="410" alt="image" src="https://github.com/user-attachments/assets/1cdd46a6-531e-4b44-8675-c3dc2802f894" />

in Ghidra

**Opcodes List**

| **Opcode** | **Mnemonic** | **Operands** | **Description** |
| --- | --- | --- | --- |
| `0x01` | **MOV** | `[R] [V]` | `regs[R] = V` |
| `0x02` | **ADD** | `[D] [S]` | `regs[D] += regs[S]` (Overflows allowed) |
| `0x03` | **XOR** | `[D] [S]` | `regs[D] ^= regs[S]` |
| `0x04` | **CMP** | `[R] [V]` | `ZF = (regs[R] == V)` |
| `0x05` | **JMP** | `[L] [H]` | Unconditional Jump to address `(H<<8)|L` |
| `0x06` | **JNE** | `[L] [H]` | Jump to Address if **Not Equal** (!ZF) |
| `0x07` | **PUTC** | `[R]` | Print character in `regs[R]` |
| `0x08` | **GETC** | `[R]` | Read character into `regs[R]` |
| `0xFF` | **HALT** | - | Stop execution |

**Critical Discovery:** Initially, we mistook opcode `0x06` for `JE` (Jump if Equal). However, dynamic analysis showed that the code jumps to the "Access Denied" routine immediately after a *successful* comparison if we treat it as `JE`. Therefore, `0x06` acts as a guard clause: "If input is WRONG, jump to failure." This makes it a **JNE** (Jump if Not Equal).

## 3. Analyzing the Bytecode (`virtue`)

We wrote a Python disassembler to inspect the `virtue` file.

0000: JMP  006e
...
006e: PUTC ... (Prints "Enter flag: ")
00f5: GETC reg[0]
00f7: XOR  reg[226], reg[222]
...
011e: CMP  reg[1], 223
0121: JNE  0003  <-- Jump to failure if wrong

The logic follows a repeating pattern:

1. **Input:** Ask for a character (`GETC`).
2. **Obfuscation:** Perform a series of XOR/ADD operations on the input using current register states.
3. **Check:** Compare the result against a hardcoded value (`CMP`).
4. **Guard:** If the comparison fails, jump to address `0003` (which prints "Tet-tot!" and quits).

## 4. Solution: VM Emulation & Brute-Force

Because the mathematical operations between the Input and the Check depend on the global state of the registers, statically reversing the math for the whole flag would be tedious.

Instead, we wrote a solver that **emulates the VM**.

1. It runs the code until it hits a `GETC` instruction.
2. It snapshots the VM state (registers + PC).
3. It tries every printable character (ASCII 32-126) as input.
4. For each character, it speculatively runs the VM forward up to 500 instructions looking for a `CMP` instruction.
5. If a character causes the `CMP` to match (`ZF=True`), we know it's the correct flag character.
6. We commit that character to the real VM state and move to the next one.

**The Solver Script (`solve.py`)**

```php
import sys

def solve():
    try:
        with open("virtue", "rb") as f:
            code = f.read()
    except FileNotFoundError:
        print("Error: 'virtue' file not found.")
        return

    regs = [0] * 256
    pc = 0
    zf = False # Zero Flag
    flag = ""
    
    print("Brute-forcing the flag... (Wait for it)")
    print("-" * 40)

    while pc < len(code):
        op = code[pc]
        
        # --- Handle Input (The Magic Part) ---
        if op == 0x08: # GETC reg
            reg_idx = code[pc+1]
            found_char = None
            
            # Snapshot state
            saved_regs = list(regs)
            saved_pc = pc + 2 # Skip the GETC instruction
            
            # Try every printable character
            for candidate in range(32, 127): 
                curr_regs = list(saved_regs)
                curr_regs[reg_idx] = candidate
                curr_pc = saved_pc
                curr_zf = False
                
                match = False
                
                # Run speculatively to find the next check
                steps = 0
                while steps < 500: # Increased step limit just in case
                    if curr_pc >= len(code): break
                    cop = code[curr_pc]
                    
                    if cop == 0x01: # MOV
                        curr_regs[code[curr_pc+1]] = code[curr_pc+2]
                        curr_pc += 3
                    elif cop == 0x02: # ADD
                        r1, r2 = code[curr_pc+1], code[curr_pc+2]
                        curr_regs[r1] = (curr_regs[r1] + curr_regs[r2]) & 0xFF
                        curr_pc += 3
                    elif cop == 0x03: # XOR
                        r1, r2 = code[curr_pc+1], code[curr_pc+2]
                        curr_regs[r1] ^= curr_regs[r2]
                        curr_pc += 3
                    elif cop == 0x04: # CMP
                        # We want the character that makes the CMP equal (ZF=True)
                        r1, val = code[curr_pc+1], code[curr_pc+2]
                        if curr_regs[r1] == val:
                            match = True
                        break # Found the check, stop this path
                    elif cop == 0x05: # JMP
                        low, high = code[curr_pc+1], code[curr_pc+2]
                        curr_pc = (high << 8) | low
                        continue
                    elif cop == 0x06: # JNE (Jump if Not Equal)
                        # Speculative path: just skip past logic, we only care about CMP
                        curr_pc += 3
                    elif cop == 0x07: # PUTC
                        curr_pc += 2
                    elif cop == 0x08: # GETC
                        break
                    elif cop == 0xFF: # HALT
                        break
                    else:
                        curr_pc += 1
                    steps += 1
                
                if match:
                    found_char = chr(candidate)
                    break
            
            if found_char:
                sys.stdout.write(found_char)
                sys.stdout.flush()
                flag += found_char
                # Commit valid state
                regs[reg_idx] = ord(found_char)
                pc += 2
                continue
            else:
                print(f"\n[!] Failed to find valid char for input at {pc:04x}")
                break

        # --- Standard Execution ---
        if op == 0x01: # MOV
            regs[code[pc+1]] = code[pc+2]
            pc += 3
        elif op == 0x02: # ADD
            r1, r2 = code[pc+1], code[pc+2]
            regs[r1] = (regs[r1] + regs[r2]) & 0xFF
            pc += 3
        elif op == 0x03: # XOR
            r1, r2 = code[pc+1], code[pc+2]
            regs[r1] ^= regs[r2]
            pc += 3
        elif op == 0x04: # CMP
            r1, val = code[pc+1], code[pc+2]
            zf = (regs[r1] == val)
            pc += 3
        elif op == 0x05: # JMP
            low, high = code[pc+1], code[pc+2]
            pc = (high << 8) | low
        elif op == 0x06: # JNE (Jump if Not Equal)
            low, high = code[pc+1], code[pc+2]
            dest = (high << 8) | low
            # FIX: Only jump if ZF is False (Not Equal)
            if not zf: 
                pc = dest
            else:
                pc += 3
        elif op == 0x07: # PUTC
            pc += 2
        elif op == 0xFF: # HALT
            print("\n\nVM Halted.")
            break
        else:
            pc += 1

    print(f"\n\nFinal Flag: {flag}")

if __name__ == "__main__":
    solve()

```

## 5. The Flag

Running the script produced the final flag:

<img width="917" height="179" alt="image" src="https://github.com/user-attachments/assets/8513da10-df75-464f-b610-9eb8cb2c68ed" />

`RE:CTF{Above_all___remember_that_God_looks_for_solid_virtues_in_us___such_as_patience___humility___obedience___abnegation_of_your_own_will_-_that_is___the_good_will_to_serve_Him_and_our_neighbor_in_Him____His_providence_allows_us_other_devotions_only_insofar_as_He_sees_that_they_are_useful_to_us___requiiem_wuzz_here}`
