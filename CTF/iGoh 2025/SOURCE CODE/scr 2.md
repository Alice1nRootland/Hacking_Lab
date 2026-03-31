# scr 2

<img width="501" height="427" alt="image" src="https://github.com/user-attachments/assets/8a46acd4-04a7-48e5-bc54-6143bfaa4ac7" />

# CTF Writeup — scr2 (50 pts)

### **Category:** Web

### **Difficulty:** Easy

### **Objective:** Analyse the server code and identify the vulnerability.

**Flag format:** `igoh25{md5(vuln)+1}`

Example: if vuln = `rce` → hash the string `rce1`.

---

# Challenge Overview

We are given a small Node.js application using Express and EJS templates.

`scr2.js`:

```jsx
const express = require('express');
const app = express();

app.set('view engine', 'ejs');

app.get('/', (req, res) => {
  res.render('index', { user_input: req.query.user_input });
});

app.listen(3000, () => {
  console.log('Server is running on port 3000');
});

```

The template:

```html
<html>
  <body>
    <%- user_input %>
  </body>
</html>

```

The challenge asks us to **analyse the source**, identify the **vulnerability**, and compute the flag.

---

#  Step-by-Step Analysis

### **1. Input source**

The parameter `req.query.user_input` is taken directly from the URL:

```
/?user_input=...
```

### **2. Output sink**

Inside the EJS template, the value is rendered using:

```
<%- user_input %>
```

In EJS:

- `<%= ... %>` → **escaped** (safe)
- `<%- ... %>` → **unescaped HTML output**

This is the dangerous one.

### **3. Result**

Any attacker-controlled content is injected straight into the HTML page **without sanitization**.

This leads to:

# Vulnerability: **Reflected Cross-Site Scripting (XSS)**

The attacker can inject HTML or JavaScript that executes in the victim’s browser.

---

# Proof of Concept (PoC)

Visiting:

```
http://localhost:3000/?user_input=<script>alert(1)</script>
```

Triggers:

```html
<script>alert(1)</script>
```

This confirms **reflected XSS**.

---

# Why It’s Vulnerable

The EJS tag `<%- %>` renders raw HTML.

Because the server directly inserts user input into the template:

```html
<%- user_input %>
```

…it executes any JavaScript provided by the attacker.

This is a classic XSS sink.

---

# Impact

- Stealing session cookies
- Defacing the page
- Forcing actions as the victim
- Pivoting to authenticated admin panels
- Full browser-based account takeover

---

#  How to Fix

Use escaped output:

```html
<%= user_input %>
```

Or sanitize the input using `sanitize-html`.

---

# 🏁 Final Flag

The challenge instructs:

> flag = igoh25{md5(vuln + "1")}
> 

Vulnerability: `xss`

Hash string: `xss1`

MD5(`xss1`) =

```
9bfaf0c2b0f3b58d5c2e159fbba7e312
```

### **Final Flag:**

```
igoh25{9bfaf0c2b0f3b58d5c2e159fbba7e312}
```
