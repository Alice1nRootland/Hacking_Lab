<img width="499" height="360" alt="image" src="https://github.com/user-attachments/assets/59981f0c-c833-41bc-9666-9098172dccd9" />


## Step 1 — Initial Analysis

We were given a PHP file `scr7.php`:

```php
private function is_valid_path( $path ) {
    return false === stripos( $path, 'phar://' );
}
```

Other methods like `file_get_contents()`, `file_exists()`, `unlink()` all call:

```php
return $this->validate_and_call(...);
```

And the validator only checks:

```php
foreach ( $args as $arg ) {
    if ( ! $this->is_valid_path( $arg ) ) {
        return false;
    }
}
```

### Observation:

- The developer tried to **block PHP object injection / phar deserialization**.
- The check only blocks the exact string `phar://`.
- Other file stream wrappers and path tricks are **not blocked**.

---

## Step 2 — Identifying the Vulnerability

The flaw is **inadequate path validation**, allowing:

- Local File Inclusion (LFI)
- Remote File Inclusion (RFI) if misconfigured
- Bypass using alternative stream wrappers: `php://`, `file://`, `zip://`, etc.

This is **classical Path Traversal / LFI vulnerability**.

---

## Step 3 — Confirming the Vulnerability

We can abuse `file_get_contents()` or other functions with:

```php
php://filter/convert.base64-encode/resource=/etc/passwd
```

Or any arbitrary local file:

```php
file_get_contents("/etc/passwd")
```

Because the code only blocks `phar://`:

```php
return false === stripos($path, 'phar://');
```

All other schemes are allowed → **Path Traversal / LFI confirmed**.

---

## Step 4 — Constructing the Flag

The challenge asks for:

```
igoh25{md5(vuln_name)}
```

Where `vuln_name` is the type of vulnerability.

Here, the **vuln name is**:

```
pathtraversal
```

So we calculate its MD5:

<img width="887" height="93" alt="image" src="https://github.com/user-attachments/assets/40f4dd59-bb0f-4106-bc70-ed0772d16465" />

```bash
echo -n "pathtraversal" | md5sum
```

Output:

```
0a7b82f000a907db5999f40dc9af621f
```

---

## Step 5 — Submit the Flag

Flag:

```
igoh25{0a7b82f000a907db5999f40dc9af621f}
```
