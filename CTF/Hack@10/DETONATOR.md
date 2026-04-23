<img width="502" height="850" alt="image" src="https://github.com/user-attachments/assets/027aeef2-f552-4bfd-b955-19c5bb7e72c2" />

ANALYZE IT USING 

<img width="1142" height="789" alt="image" src="https://github.com/user-attachments/assets/f3167822-15e6-4dec-b5b5-21bfa059cc0f" />


ghidra

check on 

<img width="478" height="626" alt="image" src="https://github.com/user-attachments/assets/a772db30-a4df-4e4a-b4bf-99428c1e85ae" />

Looking at this decompiled binary, I can see what's happening in `check_flag()`:

The program checks if a file exists at `C:\Users\HACK10{f4k3_fl4g_bu7_y0u_4r3_in_7h3_righ7_7r4ck}\Desktop\local.txt`. If the file exists, it computes `md5(filepath)` and prints `HACK10{<md5_of_filepath>}`.

So the real flag is the MD5 of the file path string

Here's the logic chain:

1. `check_flag()` hardcodes the filepath `C:\Users\HACK10{...fake flag...}\Desktop\local.txt`
2. It calls `stat64i32()` to check if that file exists — if it does, it runs `md5(filepath)` and prints the result wrapped in `HACK10{}`
3. The fake flag embedded in the path is a red herring; the **real** flag is the MD5 of the full path string itself

**`HACK10{be029cf0e9f2eaa5f80489343630befb}`**
