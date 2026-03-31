<img width="500" height="425" alt="image" src="https://github.com/user-attachments/assets/3aa95279-512a-452c-bf4c-0b5bb2e9a63c" />
# **CTF Challenge Write-Up: Insecure Java Deserialization (SCR 5)**

**Challenge Description:**

We were given a Java servlet (`mid.java`) which accepts a POST parameter `data`, decodes it from Base64, and directly calls `ObjectInputStream.readObject()`:

```java
byte[] decoded = Base64.getDecoder().decode(payload);
ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(decoded));
Object obj = ois.readObject();
```

Inside the same file, there’s a class `CommandExec` implementing `Serializable`:

```java
static class CommandExec implements Serializable {
    private String cmd;

    public CommandExec(String cmd) {
        this.cmd = cmd;
    }

    private void readObject(ObjectInputStream in) throws Exception {
        in.defaultReadObject();
        Runtime.getRuntime().exec(cmd);
    }
}
```

---

## **Vulnerability Analysis**

1. The servlet **deserializes user-supplied input without validation**.
2. The `CommandExec` class defines a `readObject` method that executes arbitrary commands during deserialization:

```java
Runtime.getRuntime().exec(cmd
```

1. This is a textbook **Java Insecure Deserialization** vulnerability.
2. An attacker can craft a malicious serialized object (or just name the vulnerability for CTF) to gain **remote code execution (RCE)**.

---

## **CTF Flag Format**

The challenge requested:

```
flag: igoh25{md5(vuln)+1}
```

- We need the **vulnerability keyword + 1**, then compute its MD5 hash.

---

## **Step 1: Identify the Vulnerability Name**

From the code:

- The exploit occurs via `ObjectInputStream.readObject()`
- The class used is `Serializable` and executes commands
- **Vulnerability type:** `RCE` via insecure deserialization

CTF keyword: `rce1`

---

## **Step 2: Compute MD5**

```bash
echo -n "rce1" | md5sum
```

<img width="686" height="72" alt="image" src="https://github.com/user-attachments/assets/edabc9af-c852-4104-99c1-6b73cc31f904" />

Output:

```
506518a19c52e8cabb91e0701dd29986
```

---

## **Step 3: Construct the Flag**

```
igoh25{506518a19c52e8cabb91e0701dd29986}
```
