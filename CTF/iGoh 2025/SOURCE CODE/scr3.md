<img width="504" height="401" alt="image" src="https://github.com/user-attachments/assets/ea8b99f0-ed4f-4d81-b8e7-03f753e6af84" />
# CTF Writeup — scr3 (50 pts)

### **Category:** Web / API Security

### **Difficulty:** Easy–Medium

### **Goal:** Identify the vulnerability inside a Spring Boot REST API

### **Flag format:** `igoh25{md5(vuln)}`

**Correct flag:** `igoh25{fe2aa597bc29ee2afe8381ac88cb1480}`

---

# Challenge Overview

We are given a simple Java Spring Boot REST controller:

```java
@RestController
@RequestMapping("/users")
public class UserController {
    @Autowired
    private UserRepository userRepository;

    @GetMapping("/{id}")
    public User getUser(@PathVariable Long id) {
        return userRepository.findById(id).orElse(null);
    }
}

```

This endpoint fetches user data from the database based solely on the provided ID.

---

# Step-by-Step Analysis

### **1. Endpoint Behavior**

The route:

```
GET /users/{id}
```

returns the user object corresponding to the numeric `{id}`.

### **2. Missing Access Controls**

There is **no check** for:

- Authentication
- Authorization
- Ownership
- Permissions
- Role validation
- Session checking

Meaning *anyone* can request *any* user's data simply by changing the ID in the URL.

---

# Vulnerability Identified: **IDOR (Insecure Direct Object Reference)**

A subset of **Broken Access Control**, ranked #1 in OWASP Top 10.

IDOR happens when an application exposes internal object identifiers and fails to verify whether the requester is allowed to access them.

### Why this is an IDOR?

Because:

```java
return userRepository.findById(id).orElse(null);
```

returns sensitive data directly with **ZERO authorization checks**.

---

# Exploitation Example

An attacker only needs to modify the ID:

```
GET /users/1
GET /users/2
GET /users/3
GET /users/100
```

Each request leaks private details of different accounts.

If the User object contains fields like:

- username
- email
- phone number
- address
- hashed password
- roles
- personal metadata

…all of this becomes exposed.

---

# Security Impact

- Full user data enumeration
- Account takeover if tokens or reset links are exposed
- Privacy breach (PII leakage)
- Horizontal privilege escalation
- Potential GDPR/PDPA violation

This is one of the most common real‑world vulnerabilities found in APIs.

---

# Final Flag

The challenge states:

> flag = igoh25{md5(vuln)}
> 

Vulnerability: `idor`

Hash provided by challenge:

```
fe2aa597bc29ee2afe8381ac88cb1480
```

### **Final Flag:**

```
igoh25{fe2aa597bc29ee2afe8381ac88cb1480}
```
