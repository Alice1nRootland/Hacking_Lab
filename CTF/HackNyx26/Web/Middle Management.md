<img width="617" height="851" alt="image" src="https://github.com/user-attachments/assets/07dc539d-3f88-465b-bc34-25c925ef3d9e" />

#### Reconnaissance

Upon accessing the target URL, we are greeted by an "Internal Operations Dashboard." The page explicitly mentions:

> "The `/admin` console is staff-only and is gated for you before you ever reach it — no badge, no entry."
> 

Checking the `Server` response header or analyzing the source code reveals that the application is running on **Next.js**.

#### Identifying the Bottleneck

Initial attempts to access `/admin` resulted in a `307 Temporary Redirect` back to the homepage (`/`). This indicates that the request is being intercepted and redirected by a security mechanism (Middleware) before it reaches the backend application logic.

Standard attempts to bypass this using header spoofing (like `X-Forwarded-For`) failed, confirming the "gate" was not a simple IP-based restriction.

#### Exploitation

Given the framework (Next.js), the vulnerability lies in how Next.js handles internal sub-requests. Next.js uses an internal header, `x-middleware-subrequest`, to track and prevent recursive middleware loops.

By injecting this header with a crafted value, we can trick the framework into believing the request has already been processed by the middleware, causing it to skip the security gate.

```jsx
curl -v -H "x-middleware-subrequest: middleware:middleware:middleware:middleware:middleware" http://85f15280-ef79-4418-ab5a-91616024fc0a.34.143.189.39.sslip.io:8001/admin
```

<img width="1517" height="637" alt="image" src="https://github.com/user-attachments/assets/172d5980-9234-4bca-9a33-b32ab6a8b608" />

#### Results

The server responds with a `200 OK`. The body of the response contains the restricted Admin Console page, revealing the production secret:

**Flag:** `HYNX{m1ddl3w4r3_1snt_4n_4uth_b0undary}`
