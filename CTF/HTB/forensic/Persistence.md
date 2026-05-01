<img width="708" height="644" alt="image" src="https://github.com/user-attachments/assets/ea17b17e-db95-48d6-ac49-04af5cc7798a" />


## Step-by-Step Analysis

### 1. Identify the Hive Type

```jsx
file query
```

<img width="1878" height="88" alt="image" src="https://github.com/user-attachments/assets/08e73c30-b6d7-466a-917c-972c58e8d234" />

Confirms it's a valid Windows Registry hive—likely `NTUSER.DAT` or `SOFTWARE`.

### Extract Strings for Quick Triage

```jsx
strings query | grep -Ei 'run|startup|powershell|cmd|wscript|dispfilename'
```

<img width="1858" height="296" alt="image" src="https://github.com/user-attachments/assets/a72034ec-f260-496a-beb8-2716c7ee5f73" />

<img width="1863" height="333" alt="image" src="https://github.com/user-attachments/assets/1a4f84f0-f73b-4abd-bdb0-72e174bf3c25" />

- Multiple `DispFileName` entries
- PowerShell paths:
    
    Code
    
    `%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe
    %SystemRoot%\SysWOW64\WindowsPowerShell\v1.0\powershell.exe`
    
- Registry keys like `RunOnce`, `Startup`, `ExplorerStartupTraceRecorded`

These suggest PowerShell-based persistence or user activity.

### Load Hive in Registry Explorer

**Path to investigate:**

```jsx
Software\Microsoft\Windows\CurrentVersion\Run
```

<img width="1211" height="739" alt="image" src="https://github.com/user-attachments/assets/74d5cb69-db63-4557-860b-3f09efadccdb" />

after few minutes of searching hahahah

Randomized binary name in `System32` is a strong indicator of malware or a dropper.

### Decode the Payload

Using further string analysis and timestamp correlation, the obfuscated binary led to a hidden flag embedded in the registry:

<img width="986" height="579" alt="image" src="https://github.com/user-attachments/assets/e8117ceb-f23e-435f-a632-f7c1ec256345" />

`HTB{1_C4n_kw3ry_4LR19h7}`

Flag captured!
