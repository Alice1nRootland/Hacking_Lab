<img width="587" height="545" alt="image" src="https://github.com/user-attachments/assets/84022681-1ee5-4a2a-b395-ee2d88e811e1" />

#### Binary Identification

First, we analyze the type of the binary:

<img width="1490" height="102" alt="image" src="https://github.com/user-attachments/assets/e8b2f160-8726-4eda-b64e-d7f96b4b1602" />


Checking strings in the binary reveals references to standard Lua virtual machine functions (`lua_pcall`, `luaL_loadbufferx`, `lua_newstate`, etc.) and a custom-named data symbol `chall_luau`:

<img width="517" height="371" alt="image" src="https://github.com/user-attachments/assets/970f7aad-5c43-446b-a1be-af4abd9ffcab" />


This indicates the binary compiles and executes an embedded Lua script at runtime.

---

#### Extracting the Lua Bytecode

We query the symbol table of the binary to locate the embedded Lua bytecode data and its length:

<img width="455" height="90" alt="image" src="https://github.com/user-attachments/assets/25275afd-f46b-4514-8d88-c6285b015e16" />


Based on section headers, the virtual address maps to offsets in the file:

- `chall_luau` is at offset `0x3f310`
- `chall_luau_len` is at offset `0x3fd90`

By reading the 8-byte little-endian integer at offset `0x3fd90`, we find the size of the bytecode is **2685 bytes**. We can then write a quick python script to extract the bytecode:

```python
with open('chall', 'rb') as f:
    f.seek(0x3f310)
    bytecode = f.read(2685)
    with open('extracted.luac', 'wb') as out:
        out.write(bytecode)
```

Running `file` on the extracted bytecode confirms it is compiled Lua 5.4 bytecode:

<img width="452" height="75" alt="image" src="https://github.com/user-attachments/assets/990a9f0f-36ff-46a2-9a75-42aa908dcecb" />

---

#### Decompilation

Using the standard Lua 5.4 decompiler `unluac`, we decompile the extracted bytecode back into readable Lua source code:

```bash
$ java -jar unluac.jar extracted.luac > decompiled.lua
```

Checking `decompiled.lua` yields the constraint-checking logic:

```lua
local flag_len = 34
-- ... [helpers like xor_byte, rot47, base64_encode] ...
local input = io.read("*line")
input = input:gsub("%s+", "")
if #input ~= flag_len then os.exit() end

-- Prefix and Suffix check
local prefix = table.concat(arr, "", 1, 5)
if "HNYX{" ~= prefix then os.exit() end
if "}" ~= arr[34] then os.exit() end

-- Underscore placements (1-indexed)
if 95 ~= string.byte(arr[10]) or 95 ~= string.byte(arr[19]) or 95 ~= string.byte(arr[23]) then os.exit() end

-- Part 1: XOR constraint
local expected_xor = { 56, 33, 53, 97 }
for i = 1, 4 do
  local b = xor_byte(arr[i + 5], 84)
  if b ~= expected_xor[i] then os.exit() end
end

-- Part 2: Reversed string check
local part_rev = table.concat(arr, "", 11, 18)
if part_rev:reverse() ~= "3d0c3tyb" then os.exit() end

-- Part 3: ROT47 check
local rot_part = table.concat(arr, "", 20, 22)
if "8_E" ~= rot47(rot_part) then os.exit() end

-- Part 4: Base64 check
local b64_part = table.concat(arr, "", 24, 33)
local expected_b64 = "ZDNjMG1waWwzZA=="
if base64_encode(b64_part) ~= expected_b64 then os.exit() end
```

---

#### Reconstructing the Flag

We reverse each constraint step by step:

1. **Prefix & Suffix**: `HNYX{` at indices 1–5, and `}` at index 34.
2. **Underscores**: `_` at indices 10, 19, and 23.
3. **Part 1 (Indices 6–9)**: XOR elements `[56, 33, 53, 97]` with `84`:
    - $56 \oplus 84 = 108$ (`l`)
    - $33 \oplus 84 = 117$ (`u`)
    - $53 \oplus 84 = 97$ (`a`)
    - $97 \oplus 84 = 53$ (`5`)
    - **Result**: `lua5`
4. **Part 2 (Indices 11–18)**: Reverse of `"3d0c3tyb"`:
    - **Result**: `byt3c0d3`
5. **Part 3 (Indices 20–22)**: ROT47-encoded string equal to `"8_E"`. Since ROT47 is self-inverse:
    - `ROT47("8_E")` $\rightarrow$ `g0t`
    - **Result**: `g0t`
6. **Part 4 (Indices 24–33)**: Base64 decode `"ZDNjMG1waWwzZA=="`:
    - **Result**: `d3c0mpil3d`

Putting all components together in their respective index positions:
`HNYX{` + `lua5` + `_` + `byt3c0d3` + `_` + `g0t` + `_` + `d3c0mpil3d` + `}`

---

#### Flag

**`HNYX{lua5_byt3c0d3_g0t_d3c0mpil3d}`**
