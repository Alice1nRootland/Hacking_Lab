<img width="503" height="543" alt="image" src="https://github.com/user-attachments/assets/12289d79-f95e-4fb0-9899-c0250246a9aa" />

i check the file and use string 

<img width="905" height="617" alt="image" src="https://github.com/user-attachments/assets/954c3eee-639e-4ae8-b59d-381483877eb3" />

i throw it to chatgpt 

<img width="874" height="589" alt="image" src="https://github.com/user-attachments/assets/5e53f913-e48b-4292-9d24-93d74c0f4478" />

and get suggestion to use dnspy 

after lomg chatgpt give me this script 

```sql
#!/usr/bin/env python3
# decode_caspian.py
# Decode custom Base64 (TestBase64.Base64Decoder alphabet) + fallbacks (std base64, rot13)
# Usage:
#   python decode_caspian.py --str "JZG1KFGoKkG1JZGxK..."
#   python decode_caspian.py --file fields.txt
#   fields.txt lines: profile=JZG1KFGo...  or just the encoded string per line

import sys, argparse, base64, binascii, codecs, re

# custom alphabet exactly as in char2sixbit array in the decompiled code
CUSTOM_ALPHABET = [
    'q','g','D','k','P','I','E','l','u','p','h','e','J','K','Q','R',
    'z','j','Y','F','G','A','m','y','C','L','w','T','W','X','v','n',
    'c','i','s','Z','b','B','U','M','N','O','S','a','t','r','V','d',
    'x','H','f','o','0','1','2','3','4','5','6','7','8','9','+','/'
]
CHAR_TO_SIX = {c: i for i, c in enumerate(CUSTOM_ALPHABET)}

def decode_custom_b64(s: str) -> bytes:
    """Decode using the custom 64-char alphabet (mimics TestBase64.Base64Decoder)."""
    s = s.strip()
    if not s:
        return b''
    src = list(s)
    length = len(src)
    padding = 0
    # count up to 2 '=' padding chars at the end
    for i in range(2):
        if length - i - 1 >= 0 and src[length - i - 1] == '=':
            padding += 1
    blockCount = length // 4
    length2 = blockCount * 3
    arr = []
    for c in src:
        if c == '=':
            arr.append(0)
        else:
            arr.append(CHAR_TO_SIX.get(c, 0))
    array2 = bytearray(length2)
    for j in range(blockCount):
        b = arr[j*4]
        b2 = arr[j*4 + 1]
        b3 = arr[j*4 + 2]
        b4 = arr[j*4 + 3]
        b5 = (b << 2) & 0xFF
        b6 = ((b2 & 48) >> 4) & 0xFF
        b6 = (b6 + b5) & 0xFF
        b5 = ((b2 & 15) << 4) & 0xFF
        b7 = ((b3 & 60) >> 2) & 0xFF
        b7 = (b7 + b5) & 0xFF
        b5 = ((b3 & 3) << 6) & 0xFF
        b8 = (b4 + b5) & 0xFF
        array2[j*3] = b6
        array2[j*3 + 1] = b7
        array2[j*3 + 2] = b8
    length3 = length2 - padding
    return bytes(array2[:length3])

def try_standard_b64(s: str):
    try:
        return base64.b64decode(s, validate=False)
    except Exception:
        return None

def try_rot13(s: str):
    try:
        return codecs.decode(s, 'rot_13')
    except Exception:
        return None

def printable_score(b: bytes) -> float:
    # crude heuristic: proportion of printable ascii + whitespace
    if not b:
        return 0.0
    good = sum(1 for c in b if 32 <= c <= 126 or c in (9,10,13))
    return good / len(b)

def pretty_print_result(name: str, enc: str):
    print("----")
    if name:
        print(f"[{name}]")
    else:
        print("[input]")
    print("encoded:", enc)
    # 1) custom decode
    try:
        out_custom = decode_custom_b64(enc)
    except Exception as e:
        out_custom = None
        print("custom decode error:", e)
    if out_custom is not None:
        score = printable_score(out_custom)
        if score > 0.6:
            try:
                print("custom decode (utf8):\n", out_custom.decode('utf-8', errors='strict'))
            except Exception:
                print("custom decode (bytes hex):", out_custom.hex())
        else:
            # show both utf8-as-best and hex
            try:
                print("custom decode (utf8, permissive):\n", out_custom.decode('utf-8', errors='replace'))
            except:
                pass
            print("custom decode (hex):", out_custom.hex())
    # 2) try standard base64
    out_std = try_standard_b64(enc)
    if out_std is not None:
        score = printable_score(out_std)
        if score > 0.6:
            try:
                print("std base64 decode (utf8):\n", out_std.decode('utf-8', errors='strict'))
            except Exception:
                print("std base64 decode (bytes hex):", out_std.hex())
        else:
            try:
                print("std base64 decode (utf8, permissive):\n", out_std.decode('utf-8', errors='replace'))
            except:
                pass
            print("std base64 decode (hex):", out_std.hex())
    # 3) rot13 (text-level)
    out_rot13 = try_rot13(enc)
    if isinstance(out_rot13, str) and out_rot13 != enc:
        print("rot13 (text):", out_rot13)
    print("----\n")

def parse_file(path: str):
    results = []
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            # accept key=val or just val
            if '=' in line:
                k, v = line.split('=', 1)
                k = k.strip()
                v = v.strip()
            else:
                k = ''
                v = line
            results.append((k, v))
    return results

def main():
    ap = argparse.ArgumentParser(description="Decode custom Caspian/TestBase64-encoded strings")
    ap.add_argument('--str', '-s', nargs='*', help='One or more encoded strings to decode')
    ap.add_argument('--file', '-f', help='Text file with lines key=encoded or just encoded per line')
    args = ap.parse_args()
    todo = []
    if args.str:
        for s in args.str:
            todo.append(('', s))
    if args.file:
        todo.extend(parse_file(args.file))
    if not todo:
        ap.print_help()
        sys.exit(0)
    for name, enc in todo:
        pretty_print_result(name, enc)

if __name__ == '__main__':
    main()

```

the result

<img width="1002" height="381" alt="image" src="https://github.com/user-attachments/assets/8835789a-8b3d-4505-88cc-5c3a20cb4fde" />

i paste the result to chatgpt

<img width="942" height="722" alt="image" src="https://github.com/user-attachments/assets/a426a001-72c2-496c-a390-cfc780db4d8c" />

change to md5

<img width="1023" height="138" alt="image" src="https://github.com/user-attachments/assets/980f62e8-98e2-4fea-8cc7-357c0ff64918" />

igoh25{5554d2071341a1107dc2775109681a74}

thats our final flag
