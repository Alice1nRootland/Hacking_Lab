<img width="590" height="806" alt="image" src="https://github.com/user-attachments/assets/e6786127-5001-4cfe-b75e-3e1bdab1a148" />

#### Resource Carving & Parsing

First, we analyzed the `.NET` binary structure to find where the resources are embedded. The binary contains a resource stream named `res2` containing several encrypted assets:

- `whoareu` (GIF)
- `kawfi` (GIF)
- `_0x251e` (ICO)
- `d0nut_glaz3` (Obfuscated Base64 data block)

We carved the raw `d0nut_glaz3` resource using a Python script:

```python
# extract_res2_raw.py
import struct

with open("Confused_Donut.exe", "rb") as f:
    data = f.read()

# Seek directly to the Data Section of res2
# (Calculated base address of res2 stream)
res2_offset = 0x5034

# Offset of d0nut_glaz3 raw block inside res2 (4035)
f.seek(res2_offset + 4035)

# Read the raw resource block
raw_data = f.read(33863 - 4035)  # kawfi starts at 33863

with open("d0nut_glaz3_raw.bin", "wb") as out:
    out.write(raw_data)
```

Run this script:

```bash
python3 extract_res2_raw.py
```

---

#### Reversed Base64 Decoding

Decompiling the main assembly metadata strings revealed that the program loads `d0nut_glaz3` and performs:

1. `ToCharArray()`
2. `Array.Reverse()`
3. `Convert.FromBase64String()`

Since the Base64 string is stored backwards, we wrote a script to reverse and decode it:

```python
# decode_b64.py
import base64

with open("d0nut_glaz3_raw.bin", "rb") as f:
    data = f.read()

# Exclude the 4-byte padding suffix from the resources struct
b64_str = data[:-4]

# Reverse the base64 string
reversed_b64 = b64_str[::-1]

# Decode base64 bytes to get the raw shellcode
decoded = base64.b64decode(reversed_b64)

with open("decoded_d0nut.bin", "wb") as out:
    out.write(decoded)
```

Run the decoding script:

```bash
python3 decode_b64.py
```

---

#### Decrypting the Donut Shellcode

The decoded output `decoded_d0nut.bin` is a position-independent shellcode compiled using the **Donut loader framework**. We used `donut-decryptor` to automatically locate the instance configurations and decrypt the module.

First, install `donut-decryptor`:

```bash
pip install donut-decryptor --break-system-packages
```

Run the decryptor on the shellcode payload:

```bash
/home/kali/.local/bin/donut-decryptor --outdir decrypted_donut_out decoded_d0nut.bin
```

This decrypted the nested payload assembly and output it to:
`decrypted_donut_out/mod_decoded_d0nut.bin`

---

#### Decompiling the Payload

The decrypted file `mod_decoded_d0nut.bin` is a standard 32-bit .NET DLL. We decompiled it using `ilspycmd` to view the original source code:

First, install `ilspycmd`:

```bash
dotnet tool install -g ilspycmd --version 8.2.0.7535
```

Decompile the DLL:

```bash
~/.dotnet/tools/ilspycmd -o decompiled_payload decrypted_donut_out/mod_decoded_d0nut.bin
```

---

#### Extracting the Flag

Inspecting the decompiled source file `decompiled_payload/mod_decoded_d0nut.decompiled.cs`, we see the `Flag` class:

```csharp
namespace Payload;

public class Flag
{
	public static void Run()
	{
		RegistryKey registryKey = Registry.CurrentUser.OpenSubKey("SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion", writable: true);
		if (registryKey != null)
		{
			registryKey.SetValue("Flag", "HNYX{c0nfu$1nG_tH3_d0nUt_4_c0ff33}");
			registryKey.Close();
		}
	}
}
```

The flag is written to the registry path `HKCU\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Flag`.

**Flag:** `HNYX{c0nfu$1nG_tH3_d0nUt_4_c0ff33}`
