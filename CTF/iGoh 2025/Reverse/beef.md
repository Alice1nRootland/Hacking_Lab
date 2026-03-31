<img width="493" height="423" alt="image" src="https://github.com/user-attachments/assets/103f40b5-148a-4c8c-8dc0-f7dc57898d28" />

**Challenge Name:** Beef
**Category:** Reverse Engineering

### 1. Initial Analysis

We started by analyzing the binary using GDB to understand its structure. Since the binary had no debugging symbols (`(No debugging symbols found)`), we listed the available functions to find the entry point and any interesting custom functions.

Bash

`gdb -q ./beef
(gdb) info functions`

<img width="659" height="484" alt="image" src="https://github.com/user-attachments/assets/e757dbe5-11d9-45b4-ace1-fec85d6dc721" />

**Observation:**
From the function list, we identified a few custom functions of interest:

- `main`: The standard entry point.
- `pFlag`: Likely a function that prints the flag.
- `red` & `blue`: Helper functions (possibly decoys or part of the logic).

### 2. Debugging & Disassembly

We set a breakpoint at `main` and ran the program. Once hit, we disassembled the `main` function to understand the control flow.

Bash

`(gdb) break main
(gdb) run
(gdb) disassemble main`

**Code Analysis:**
Looking at the assembly, we found a critical comparison check at offset `<+30>` and `<+37>`:

Code snippet

`0x...52fc <+30>:   cmpl   $0xdeadbeef, -0x4(%rbp)
0x...5303 <+37>:   jne    0x55555555532a <main+76>`

- **The Check:** The program compares a local variable (located at `rbp-4`) against the hexadecimal value `0xdeadbeef`.
- **The Branch:** The `jne` (Jump if Not Equal) instruction checks the result.
    - **If the value is NOT** `0xdeadbeef`: It jumps to `<main+76>`, effectively skipping the flag printing logic.
    - **If the value IS** `0xdeadbeef`: It continues execution to the next instruction (`<main+39>`), calls `puts`, and eventually calls `pFlag` at `<+69>`.

### 3. Exploitation (The Bypass)

Instead of trying to reverse engineer how to input the value `0xdeadbeef` into the stack variable, we decided to manipulate the instruction pointer (RIP) directly using GDB to bypass the check.

We identified the address immediately following the jump instruction. This is the "success" path where the code execution continues if the check had passed.

<img width="723" height="698" alt="image" src="https://github.com/user-attachments/assets/1cda0977-b722-4e0d-896b-72bd61edb195" />

- **Target Address:** `0x555555555305` (This corresponds to `<main+39>`).

We executed the jump command:

Bash

`(gdb) jump *0x555555555305`

### 4. Result

By forcing the instruction pointer to the address inside the success condition, the program proceeded to execute the winning logic:

1. It printed "passed?:".
2. It executed `call pFlag`.
3. The flag was revealed.

**Flag:**

Plaintext

`igoh25{WHy_It_1o0KS_s0_F4M1li4r?}`

convert into md5

9af63754e56936dd0f0088a5c4488850

Final answer : igoh25{9af63754e56936dd0f0088a5c4488850}
