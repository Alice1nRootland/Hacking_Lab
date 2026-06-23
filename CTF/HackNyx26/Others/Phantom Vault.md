<img width="617" height="847" alt="image" src="https://github.com/user-attachments/assets/73158e6a-c80c-4fa4-b577-10131e8fd53e" />

The flag is **`HNYX{D0ubl3_d3c0y_runt1m3_l0g1c}`**.

---

### How it was recovered

1. From `runtime.log`:
    - `backup_size = 1337`
    - `modifier = file_size % 17 = 1337 % 17 = 11`
    - The active transformation is the `transform(text, modifier)` function.
2. The encrypted vault (`vault.enc`) contains:
    
    ```
    SDTX{N0oap3_w3f0l_owuf1i3_w0b1h}
    ```
    
3. The `transform` function applies a per‑character shift:
    
    ```
    shift = ((i * 5) + modifier) % 26
    ```
    
    only to alphabetic characters; non‑letters are left unchanged.
    
4. To decrypt, subtract `shift` from each letter (with modulo 26). Doing this yields:
    
    ```
    HNYX{D0ubl3_d3c0y_runt1m3_l0g1c}
    ```
    

This matches the required flag format `HNYX{}`.

right away from deepseek.
