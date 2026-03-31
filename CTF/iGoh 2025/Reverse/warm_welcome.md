<img width="490" height="422" alt="image" src="https://github.com/user-attachments/assets/4c806f58-9485-45c7-b204-60113c565d65" />

**Challenge Name:** Warm Welcome

**Category:** Reverse Engineering

**Tools Used:** GDB (GNU Debugger)

## Objective

The goal of this challenge is to obtain the flag hidden within the `warm_welcome` binary. The program asks for a "license" key, validates it, and presumably grants access if the key is correct.

## Analysis

<img width="943" height="77" alt="image" src="https://github.com/user-attachments/assets/f64023cf-7377-4e5d-9dae-ef94b5116224" />

### 1. Initial Reconnaissance

We started by loading the binary into GDB to understand its structure. Using the `info functions` command, we listed the symbols present in the binary.

```
(gdb) info functions

```

We observed standard C library functions like `printf`, `fgets`, and `strcspn`, along with the `main` function at address `0x1080`. This confirms it is a standard C program reading user input.

### 2. Static Analysis & Disassembly

Next, we disassembled the `main` function to understand the logic flow.

<img width="467" height="387" alt="image" src="https://github.com/user-attachments/assets/0d1b4210-319b-4307-a2db-2574e535ea50" />

```
(gdb) disassemble main

```

From the assembly code (seen in the second screenshot), we noticed a few key behaviors:

- **Input Reading:** `fgets` is called to read user input.
- **Length Check:** There is a comparison `cmp $0xe, %rax` (0xe is 14 in decimal). This suggests the program expects a license key of exactly **14 characters**.
- **Validation Loop:** The code enters a loop that performs various arithmetic operations (`xor`, `mul`, `add`, `rol`) on the input string to validate the key.

### 3. The Bypass Strategy

Reverse engineering the exact mathematical algorithm to generate a valid key is one valid approach. However, a faster method is **runtime manipulation**.

Instead of finding the correct key, we can force the program to jump to the "Success" branch regardless of whether our input is correct.

Looking at the program execution flow:

1. The program checks the input.
2. It performs a check (likely a `test` or `cmp` instruction followed by a conditional jump like `je` or `jne`).
3. If the check fails, it prints "invalid".
4. If the check passes, it prints "ACCESS GRANTED" and the flag.

## Exploitation

We decided to use GDB to manually hijack the instruction pointer (RIP) during runtime.

**Step 1: Set a Breakpoint**
We identified a critical point in the execution flow near the end of the validation logic. We set a breakpoint at `*main+186`.

```
(gdb) break *main+186

```

**Step 2: Provide Input**
We ran the program. Knowing the length check we saw earlier (`0xe`), we provided a dummy input of 14 characters to satisfy the initial length requirement.

```
Enter license: AAAAAAAAAAAAAA

```

**Step 3: Hijack Execution**
The program hit our breakpoint at `*main+186`. At this stage, the program was about to evaluate our invalid input and likely jump to the failure message.

To bypass this, we manually forced the instruction pointer to jump forward to `*main+188`, effectively skipping the failure check/branch.

```
(gdb) jump *main+188

```

**Result:**
The program skipped the validation failure and executed the code block responsible for success.

```
Continuing at 0x55555555513c.
ACCESS GRANTED
flag:igoh25{hel10_w0rld_42}

```

## Conclusion

By identifying the success branch and manually manipulating the instruction pointer in GDB, we bypassed the complex license validation algorithm entirely.

Convert `hel10_w0rld_42` into md5 : 6aa8c76e0b4d6ddc1e03a2e822506044

**Flag:** igoh25{6aa8c76e0b4d6ddc1e03a2e822506044}
