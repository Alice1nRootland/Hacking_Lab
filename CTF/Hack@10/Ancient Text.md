<img width="614" height="652" alt="image" src="https://github.com/user-attachments/assets/94e6c29b-b474-4ce4-bdaa-5fb1114a4dda" />

# Initial Analysis

The challenge provided an image containing several lines of unusual symbols mixed with characters that resembled mathematical notation. At first glance, the text looked like some form of symbolic cipher.

Initially, I considered that the symbols might correspond to common classical ciphers such as:

- Caesar cipher
- Substitution cipher
- Atbash cipher

However, the characters did not map cleanly to any typical cipher alphabet.

---

# Identifying the Script

<img width="1280" height="566" alt="image" src="https://github.com/user-attachments/assets/af392926-84a2-42f6-9f08-2e4742c9f152" />

Looking more closely at the challenge description, two hints stood out:

- The reference to **Frieren and her party**
- The phrase **ancient text left by an elf**

These clues suggested a connection to **Frieren: Beyond Journey’s End**, which features an **Ancient Elven Script**.

To verify this, I searched online for:

```
Zoltraak Ancient Elven Script translate
```

This quickly led to reference images showing a **mapping between Ancient Elven symbols and the English alphabet** used in the series.

---

# Translating the Symbols

<img width="640" height="155" alt="image" src="https://github.com/user-attachments/assets/a0dad521-4752-4131-b189-a2d7b35d37ce" />

Using the reference image as a guide, I translated the symbols from the challenge **one by one**.

Applying the alphabet mapping produced the following text:

```
theflagiszoltraak
```

The message directly reveals the flag phrase.

---

# Constructing the Flag

The challenge specifies the format:

```
hack10{text}
```

Extracting the key word from the translated phrase:

```
zoltraak
```

The final flag becomes:

```
hack10{zoltraak}
```
