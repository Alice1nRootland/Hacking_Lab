<img width="615" height="538" alt="image" src="https://github.com/user-attachments/assets/530de322-7db1-4303-a01c-8445a2b494f7" />

# Initial Reconnaissance

Upon visiting the site, we are presented with a standard "Terms of Service" page. While the text is long, the challenge prompt suggests the flag is hidden within the document's structure or metadata.

I started by viewing the page source (`Ctrl+U` or `view-source:`) and noticed several developer comments that served as hints:

<img width="880" height="75" alt="image" src="https://github.com/user-attachments/assets/213365b0-9392-434f-8152-3f7225eb1c89" />

# Analysis & Exploitation

### 1. The CSS Injection

Following the hint about "audit notes in CSS," I checked the linked stylesheet: `http://34.126.187.50:5507/style.css`.

By examining the bottom of the file, I found a pseudo-element rule that injects content into the page while making it invisible to the user:

<img width="272" height="108" alt="image" src="https://github.com/user-attachments/assets/e31c5dfe-54f5-4e4e-89b2-dba18fe89cc2" />

**Flag Part 1:** `hack10{f1n3_`

### **2. The "Invisible" Fragment**

Searching the HTML source for suspicious classes mentioned in the CSS (like `.invisible-fragment`), I found a hidden span inside **Clause 19**:

<img width="905" height="133" alt="image" src="https://github.com/user-attachments/assets/b31aeef5-b5f6-4b89-a3dd-b8013585ab48" />

The CSS for this class confirmed it was hidden by matching the text color to the background color (`color: var(--doc-bg)`).

**Flag Part 2:** `pr1nt_`

### **3. The Hidden Footnote**

Finally, at the very bottom of the `doc-content` div, there was a footnote element. The CSS marked this as `display: none;`, meaning it does not render on the screen at all:

<img width="548" height="55" alt="image" src="https://github.com/user-attachments/assets/ddd48501-b336-427f-84d3-9f430777c7a4" />

**Flag Part 3:** `n3v3rr_l13ss}`

---

# Flag Construction

Combining the three pieces found in the CSS and HTML:

1. `hack10{f1n3_`
2. `pr1nt_`
3. `n3v3rr_l13ss}`

**Flag:** `hack10{f1n3_pr1nt_n3v3rr_l13ss}`
