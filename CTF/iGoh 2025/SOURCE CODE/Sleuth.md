<img width="458" height="372" alt="image" src="https://github.com/user-attachments/assets/94c17c41-4935-47d2-9e2e-38f369b4ca9f" />


### 1. Source Code Review and Vulnerable Route Discovery

The challenge provided the source code in a file named `src1.zip`. The first step was to examine the code to look for routes or functions that handle sensitive data or have weak security checks.

- **Action:** Analyze the application's source code (likely a web framework like Flask or Node.js).
- **Discovery:** A **debugging route** was identified, typically named something like `/debug`.

<img width="838" height="259" alt="image" src="https://github.com/user-attachments/assets/86e8c8ad-c0b3-4a81-8b4e-497c21497440" />



### 2. Exploiting the Logic Flaw

The logic flaw was the use of a hardcoded, easily guessable key (`letmein123`) to guard the debugging endpoint. By appending the correct key to the URL, the restriction was bypassed.

- **Target URL:** `http://3.0.177.234:5003/`
- **Action:** Access the `/debug` route and supply the guessed key as a query parameter.
- **Payload URL:** `http://3.0.177.234:5003/debug?key=letmein123`

<img width="513" height="100" alt="image" src="https://github.com/user-attachments/assets/8efde4c5-d1ee-402f-bce0-6546dc8b54fe" />

### 3. Flag Retrieval

Executing the payload URL caused the server to execute the "success" path of the debug logic, returning the flag directly in a JSON response.

- **Result:** The browser displayed the flag:

<img width="533" height="100" alt="image" src="https://github.com/user-attachments/assets/85f86a48-6ec4-42e9-bafb-8ca3980e83ac" />

### Final Flag

**`igoh25{3e01206621aa712b7db10558451d263f}`**
