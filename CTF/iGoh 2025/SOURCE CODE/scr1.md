# scr1

# CTF Writeup — scr1 (50 pts)

### **Category:** Web

### **Difficulty:** Easy

### **Flag:** `igoh25{2c71e977eccffb1cfb7c6cc22e0e7595}`

---

# Challenge Overview

We are given a very small PHP script named `scr.php`. Our task is to analyze the code, identify the vulnerability, and generate the correct flag based on the vulnerability name.

The script:

```php
<?php
// Assume $_GET['user_input'] is some input from the user
echo $_GET['user_input'];
?>
```

At first glance, it looks extremely simple — but **simplicity is often where the most classic vulnerabilities appear.**

---

# Step‑by‑Step Analysis

### **1. User Input Source**

The script reads:

```php
$_GET['user_input']
```

Meaning any attacker can supply their own input via the URL:

```
scr.php?user_input=...
```

### **2. Output Sink**

The script outputs the input directly:

```php
echo $_GET['user_input'];
There is **no:**
```

- validation
- filtering
- sanitization
- escaping

The value is printed **as‑is** to the HTML page.

---

# Vulnerability Identified — Reflected XSS

Because user input is echoed directly into the page, an attacker can inject malicious HTML or JavaScript.

### **Example XSS Payload:**

```
http://target.com/scr.php?user_input=<script>alert(1)</script>
```

The browser will execute:

```html
<script>alert(1)</script>
```

This is the textbook definition of **Reflected Cross-Site Scripting (XSS)**.

---

# Proof of Impact

Using reflected XSS, an attacker could:

- Steal session cookies
- Inject phishing content
- Execute browser-based actions as the victim
- Redirect users
- Perform full account takeover if cookies are not `HttpOnly`

This is why "echoing raw input" is one of the most dangerous mistakes in PHP applications.

---

#  How to Fix

To prevent XSS, always **escape output**:

```php
echo htmlspecialchars($_GET['user_input'], ENT_QUOTES, 'UTF-8');
```

Or sanitize:

```php
filter_input(INPUT_GET, 'user_input', FILTER_SANITIZE_SPECIAL_CHARS);
```

---

# Final Flag

The challenge states:

> flag: igoh25{md5(vuln)}
> 

Vulnerability name (lowercase):

```
xss
```

MD5("xss") =

```
2c71e977eccffb1cfb7c6cc22e0e7595
```

Therefore:

### **Flag: `igoh25{2c71e977eccffb1cfb7c6cc22e0e7595`**
