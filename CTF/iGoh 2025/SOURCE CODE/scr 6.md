<img width="502" height="358" alt="image" src="https://github.com/user-attachments/assets/18130f83-67ba-4fb0-a4a7-238d7ea3da9a" />

# scr6 – Command Injection Vulnerability

**Category:** Web / Code Review

**Flag format:** `igoh25{md5(vuln)+1}`

---

## Challenge Overview

We are given a PHP class **Text_Diff_Engine_shell** which is responsible for computing differences between two sets of text lines. The interesting part is that it uses:

```php
$diff = shell_exec($this->_diffCommand . ' ' . $from_file . ' ' . $to_file);
```

This instantly becomes suspicious because it executes a shell command constructed from a class property and file names.

---

## Vulnerability Analysis

### Vulnerability: **Command Injection**

The class contains a modifiable property:

```php
var $_diffCommand = 'diff';
```

Since this property is **public**, any caller of the class can modify it:

```php
$engine->_diffCommand = "diff; malicious_command";
```

When the code reaches:

```php
shell_exec($this->_diffCommand . ' ' . $from_file . ' ' . $to_file);
```

It becomes:

```
diff file1 file2; malicious_command file1 file2
```

Because `shell_exec()` executes the whole string directly in `/bin/sh`, whatever is appended after a semicolon will run as a separate system command.

This is a **classic command injection vulnerability**.

---

## Impact

An attacker can execute **arbitrary system commands**, such as:

- reading `/etc/passwd`
- running reverse shells
- uploading malware
- modifying system files

This gives complete server compromise.

---

## Determining the Correct Flag

The challenge states:

> flag: igoh25{md5(vuln)+1}
> 
> 
> example: `sqli1 → md5("sqli1")`
> 

So the vulnerability name must follow the same naming pattern.

The correct name is:

```
commandinjection
```

Now compute the MD5:

```bash
echo -n "commandinjection" | md5sum
```

![image.png](attachment:eee7745e-81a9-48ce-9411-684c33da5d9d:image.png)

Output:

```
8338b65cbf67143589bd16aaf038017d  -
```

---

# Final Flag

```
igoh25{8338b65cbf67143589bd16aaf038017d}
```
