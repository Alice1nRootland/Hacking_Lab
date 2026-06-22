<img width="572" height="492" alt="image" src="https://github.com/user-attachments/assets/e4e5bdc2-afb8-41b0-b80c-08d4b1db3e25" />

#### Initial Reconnaissance

We first inspected the file format of the `pacman` binary to identify its architecture and packer.

```bash
file pacman
```

**Output:**

```
pacman: PE32+ executable (GUI) x86-64, for MS Windows
```

We also scanned the strings in the binary and identified markers indicative of a **PyInstaller** packaged Python executable (e.g., `_pyinstaller_pyz`, `Py_Initialize`, and a large trailing overlay).

---

#### Extracting the PyInstaller Archive

To extract the embedded Python files, we used the `pyinstxtractor.py` utility.

```bash
python3 pyinstxtractor.py pacman
```

Because of local disk constraints and Python version differences (the binary was compiled using Python 3.12 while the system ran Python 3.13), the automatic extraction of the `PYZ.pyz` archive was skipped by `pyinstxtractor`. However, it successfully dumped the entry point `main.pyc` and `PYZ.pyz` into `/tmp/pacman_ext/pacman_extracted/`.

---

#### Compiling the Decompiler (pycdc)

Since Python 3.12 bytecode (`cb0d0d0a`) is not fully supported by older decompilers, we cloned and manually compiled the latest version of `pycdc` (Decompyle++):

```bash
git clone <https://github.com/zrax/pycdc.git> /tmp/pycdc_src
cd /tmp/pycdc_src
cmake .
make -j$(nproc)
cp pycdc /tmp/pycdc_bin
```

---

#### Decompiling the Entry Point (`main.pyc`)

We decompiled `main.pyc` using the newly compiled `pycdc` binary:

```bash
/tmp/pycdc_bin /tmp/pacman_ext/pacman_extracted/main.pyc > /tmp/pacman_ext/main_stub.py
cat /tmp/pacman_ext/main_stub.py
```

**Output:**

```python
_ = lambda __: __import__('zlib').decompress(__import__('base64').b64decode(__[::-1]))
exec(_(b'==QNP85jB8/33n//...'))
```

---

#### Deobfuscating the Nested Payloads

The lambda function reverses the base64-encoded string, decodes it, and decompresses it using `zlib`. However, the payload contained dozens of nested, recursively wrapped obfuscation layers.

We automated the unpacking process using a Python script:

```python
import zlib, base64, re

_ = lambda __: zlib.decompress(base64.b64decode(__[::-1]))

payload = b'==QNP85...'  # Initial obfuscated string

while True:
    try:
        decompressed = _(payload)
        text = decompressed.decode()
        match = re.search(r"exec\(\(_\)\(b'\"['\"]\)\)", text)
        if match:
            payload = match.group(1).encode()
        else:
            print("Final Unpacked Code:\n", text)
            break
    except Exception as e:
        print("Error during unpacking:", e)
        break
```

**Unpacked Entry Point (`main.py`):**

```python
from game import Game

if __name__ == "__main__":
    game = Game()
    game.run()
```

---

#### Extracting the `PYZ.pyz` Archive

Since the entry point imports `Game` from `game`, the actual logic is stored inside the `PYZ.pyz` archive. We wrote a script to parse the `PYZ` table of contents (TOC) and extract the custom modules:

```python
import struct, marshal, zlib, os

pyz_path = "/tmp/pacman_ext/pacman_extracted/PYZ.pyz"
dir_name = "/tmp/pacman_ext/pacman_extracted/PYZ.pyz_extracted"

with open(pyz_path, "rb") as f:
    assert f.read(4) == b"PYZ\0"
    pyz_magic = f.read(4)
    (toc_position, ) = struct.unpack("!i", f.read(4))
    f.seek(toc_position)
    toc = marshal.load(f)

    if isinstance(toc, list):
        toc = dict(toc)

    for key, (ispkg, pos, length) in toc.items():
        f.seek(pos)
        file_name = key.decode("utf-8") if isinstance(key, bytes) else key
        file_name = file_name.replace(".", os.path.sep)

        file_path = os.path.join(dir_name, file_name, "__init__.pyc") if ispkg == 1 else os.path.join(dir_name, file_name + ".pyc")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        data = zlib.decompress(f.read(length))
        with open(file_path, "wb") as out:
            # Prepend Python 3.12 header magic bytes
            out.write(b"\xcb\x0d\x0d\x0a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
            out.write(data)
```

This successfully extracted the custom game modules:

- `constants.pyc`
- `game.pyc`
- `ghost.pyc`
- `player.pyc`
- `renderer.pyc`

---

#### Deobfuscating Game Modules

Each of the extracted game modules was obfuscated using the same recursive `exec(_(b'...'))` wrapping pattern. We decompiled the files using `pycdc` and automatically ran our deobfuscation script over them.

**Decompiled `renderer.py`:**

```python
import pygame

FLAG_BITMAP = [
    [True, False, False, ...],
    ...
]
FLAG_WIDTH = 228
FLAG_HEIGHT = 7

def draw_flag_bitmap(screen, x, y, pixel_size=3, color=(255, 255, 0)):
    # Draws the flag to the pygame screen...
```

---

#### Decoding the Flag

We reconstructed the flag directly by printing the `FLAG_BITMAP` variable from `renderer.py` as an ASCII grid:

```python
from renderer import FLAG_BITMAP

for row in FLAG_BITMAP:
    print("".join("#" if pixel else " " for pixel in row))
```

**Reconstructed Output:**

```
#   # #   # #   # #   #   ##    #           ##      #       ####  #     ##### ##### ####  ####              ####  ##### #####   #   #####  ###      #                   ##### #            ###   ###      # #     #####     #  ##
#   # ##  # #   #  # #    #    ##          #        #           # #     #         #     #     #                 # #         #  ##   #     #   #     #                       # #           #   # #   #     # #     #         #   #
#   # # # #  # #    #     #     #    ###   #     ####  ###      # ####  #        #      #     #  ###   ###      # #        #    #   #     #   #  ####  ###   ###   ###     #  ####   ###  #   # #  ##  #### ####  #      ####   #
##### #  ##   #     #    #      #   #     ###   #   # #      ###  #   # ####    #    ###   ###      # #####  ###  ####    #     #   ####   ###  #   # ##### ##### #####   #   #   # #      ###  # # # #   # #   # ####  #   #    #
#   # #   #   #     #     #     #   #      #    #   # #         # #   #     #  #        #     #  #### #         #     #  #      #       # #   # #   # #     #     #      #    #   # #     #   # ##  # #   # #   #     # #   #   #
#   # #   #   #    # #    #     #   #   #  #    #   # #   #     # #   #     #  #        #     # #   # #   #     #     #  #      #       # #   # #   # #   # #   # #   #  #    #   # #   # #   # #   # #   # #   #     # #   #   #
#   # #   #   #   #   #   ##   ###   ###   #     ####  ###  ####  ####  ####   #    ####  ####   ####  ###  ####  ####   #     ###  ####   ###   ####  ###   ###   ###   #    ####   ###   ###   ###   #### ####  ####   ####  ##
```

By segmenting the columns into individual character grids, we transcribed the letters one-by-one:

- `HNYX{`
- `1` `c` `f` `d` `c` `3` `b` `5` `7` `3` `3` `a` `e` `3` `5` `7` `1` `5` `8` `d` `e` `e` `e` `7` `b` `c` `8` `0` `d` `b` `5` `d`
- `}`

The final MD5 hash inside the flag brackets is:
`1cfdc3b5733ae357158deee7bc80db5d`

---

#### Final Flag

**`HNYX{1cfdc3b5733ae357158deee7bc80db5d}`**
