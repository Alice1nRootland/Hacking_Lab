<img width="608" height="426" alt="image" src="https://github.com/user-attachments/assets/71c2fe73-38f8-420c-b538-c8b70289c574" />

# Vulnerability Analysis

The security of this cryptosystem relies on a hashing loop. Let's look at the core logic:

```bash
for i in range(0, len(flag), 2):
a = random.randint(90, 128)
b = random.randint(1, 15)
cipher = hashlib.sha512(flag[i:i+2]).hexdigest()
encrypted += binascii.hexlify(os.urandom(random.randint(0, 31))).decode('utf-8')
encrypted += cipher[b:a]
```

There are three critical weaknesses here:

1. **Small Keyspace:** The flag is processed in **2-character chunks**. Since standard ASCII characters are used, there are only $256^2 = 65,536$ possible combinations per chunk. This is small enough to brute-force in seconds.

2. **Known Algorithm:** It uses **SHA-512**, a deterministic hashing algorithm with no "salt" inside the hash function.

3. **Leaked Slices:** Although it adds random noise (`os.urandom`) and takes a slice of the hash (`cipher[b:a]`), the slice is very long (between 75 and 127 hex characters). Random noise is only up to 62 hex characters. This means the signature of the hash is always visible and unique.

# Exploitation Part

To recover the flag, we perform a **Known-Plaintext Brute Force** attack:

1. Read the `output` file and convert the binary data back into its hex string representation.
2. Iterate through the ciphertext.
3. For every possible 2-character pair (e.g., `aa`, `ab`, `ac`...), calculate the SHA-512 hash.
4. Check if a significant portion of that hash exists in the ciphertext.
5. Because the flag is processed linearly, we keep track of our "cursor" position in the ciphertext to ensure we extract the flag chunks in the correct order.

Script:

**this script automates the recovery by searching for 50-character overlaps of calculated hashes within the hex output.

`import hashlib
import string`

`#Load the encrypted data and convert to hex string`

`with open("output", "rb") as f:
data = f.read().hex()`

`#Define the search space (printable ASCII)`

`alphabet = string.printable.encode()
flag = ""
cursor = 0`

`print("Recovering flag...")`

`#Linear Brute Force`

`while cursor < len(data):
best_match = None
best_pair = ""`

`for c1 in alphabet:
    for c2 in alphabet:
        pair = bytes([c1, c2])
        full_hash = hashlib.sha512(pair).hexdigest()

        # Look for a 50-char slice of the hash in the remaining data
        # We skip the first 15 chars to account for the random 'b' offset
        target_segment = full_hash[15:65]

        if target_segment in data[cursor:]:
            match_pos = data.find(target_segment, cursor)
            if best_match is None or match_pos < best_match:
                best_match = match_pos
                best_pair = pair.decode()

if best_match is not None:
    flag += best_pair
    cursor = best_match + 50 # Advance past the found chunk
else:
    break`

`print(f"\n[+] Flag: {flag}")`

Result:

```bash
┌──(kali㉿kali)-[~/hackaten/crypto/babycrypto]
└─$ python3 [exploit.py](http://exploit.py/)
Recovering flag...
Found chunk: ha -> Flag so far: ha
Found chunk: ck -> Flag so far: hack
Found chunk: 10 -> Flag so far: hack10
Found chunk: {a -> Flag so far: hack10{a
Found chunk: 88 -> Flag so far: hack10{a88
Found chunk: da -> Flag so far: hack10{a88da
Found chunk: cd -> Flag so far: hack10{a88dacd
Found chunk: 5f -> Flag so far: hack10{a88dacd5f
Found chunk: b8 -> Flag so far: hack10{a88dacd5fb8
Found chunk: 8d -> Flag so far: hack10{a88dacd5fb88d
Found chunk: c4 -> Flag so far: hack10{a88dacd5fb88dc4
Found chunk: 97 -> Flag so far: hack10{a88dacd5fb88dc497
Found chunk: 3b -> Flag so far: hack10{a88dacd5fb88dc4973b
Found chunk: b3 -> Flag so far: hack10{a88dacd5fb88dc4973bb3
Found chunk: a5 -> Flag so far: hack10{a88dacd5fb88dc4973bb3a5
Found chunk: 6f -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56f
Found chunk: ff -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff
Found chunk: 9b -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9b
Found chunk: e9 -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be9
Found chunk: 40 -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940
Found chunk: bb -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb
Found chunk: 1f -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f
Found chunk: 1b -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b
Found chunk: 83 -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83
Found chunk: c2 -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2
Found chunk: b8 -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b8
Found chunk: 2f -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f
Found chunk: 3f -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f
Found chunk: 6d -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6d
Found chunk: aa -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa
Found chunk: 25 -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa25
Found chunk: 62 -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa2562
Found chunk: 67 -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267
Found chunk: c9 -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9
Found chunk: 78 -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c978
Found chunk: 6f -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f
Found chunk: 4c -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4c
Found chunk: dc -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc
Found chunk: 70 -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70
Found chunk: 25 -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc7025
Found chunk: 50 -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc702550
Found chunk: 79 -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70255079
Found chunk: e3 -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70255079e3
Found chunk: cf -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70255079e3cf
Found chunk: ae -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70255079e3cfae
Found chunk: a9 -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70255079e3cfaea9
Found chunk: 95 -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70255079e3cfaea995
Found chunk: 62 -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70255079e3cfaea99562
Found chunk: 11 -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70255079e3cfaea9956211
Found chunk: e6 -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70255079e3cfaea9956211e6
Found chunk: 15 -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70255079e3cfaea9956211e615
Found chunk: fe -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70255079e3cfaea9956211e615fe
Found chunk: 78 -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70255079e3cfaea9956211e615fe78
Found chunk: ee -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70255079e3cfaea9956211e615fe78ee
Found chunk: 9d -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70255079e3cfaea9956211e615fe78ee9d
Found chunk: 5a -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70255079e3cfaea9956211e615fe78ee9d5a
Found chunk: 95 -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70255079e3cfaea9956211e615fe78ee9d5a95
Found chunk: a8 -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70255079e3cfaea9956211e615fe78ee9d5a95a8
Found chunk: 32 -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70255079e3cfaea9956211e615fe78ee9d5a95a832
Found chunk: af -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70255079e3cfaea9956211e615fe78ee9d5a95a832af
Found chunk: ff -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70255079e3cfaea9956211e615fe78ee9d5a95a832afff
Found chunk: 2f -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70255079e3cfaea9956211e615fe78ee9d5a95a832afff2f
Found chunk: 09 -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70255079e3cfaea9956211e615fe78ee9d5a95a832afff2f09
Found chunk: b0 -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70255079e3cfaea9956211e615fe78ee9d5a95a832afff2f09b0
Found chunk: 5c -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70255079e3cfaea9956211e615fe78ee9d5a95a832afff2f09b05c
Found chunk: 39 -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70255079e3cfaea9956211e615fe78ee9d5a95a832afff2f09b05c39
Found chunk: db -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70255079e3cfaea9956211e615fe78ee9d5a95a832afff2f09b05c39db
Found chunk: 4} -> Flag so far: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70255079e3cfaea9956211e615fe78ee9d5a95a832afff2f09b05c39db4}
```

```bash
[+] Full Flag: hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70255079e3cfaea9956211e615fe78ee9d5a95a832afff2f09b05c39db4}
```

# Conclusion

The script successfully reconstructs the flag by matching the fragments of SHA-512 hashes buried between random bytes.

**hashing small inputs without a unique salt per-block is not secure, as the entire input space can be precomputed or brute-forced.

**Flag:**`hack10{a88dacd5fb88dc4973bb3a56fff9be940bb1f1b83c2b82f3f6daa256267c9786f4cdc70255079e3cfaea9956211e615fe78ee9d5a95a832afff2f09b05c39db4}`
