<img width="496" height="544" alt="image" src="https://github.com/user-attachments/assets/af5bed6a-ba1c-42cd-8919-04d15dea3d1c" />

#### Initial Triage

Initial inspection using the `strings` utility identified several suspicious objects within the PDF structure.

- **Trigger Mechanism:** Object 1 contained an `/OpenAction` attribute pointing to Object 5, ensuring immediate execution upon opening.
- **Metadata Discrepancy:** The PDF metadata listed the author as "Luann Barnes" and the producer as "Acrobat Distiller 5.0.5," a common tactic to make the file appear aged and legitimate.

<img width="1420" height="657" alt="image" src="https://github.com/user-attachments/assets/0ca581c7-a20a-49f2-b23d-da67523078db" />

## Static Analysis & Technical Breakdown

### A. Extracting the Stager

Using `mutool show resume.pdf 5`, the following JavaScript was isolated:

<img width="1120" height="165" alt="image" src="https://github.com/user-attachments/assets/1b74bbe8-62c2-4d58-89b3-e77070db9672" />

**Technical Analysis:**

1. The script concatenates two arrays to form the string: `BOPCd0edrK 1i+mVBeXU8:ddd$`.
2. The `atob()` function is called, but despite the name suggesting Base64, the character set and structure indicated **Base85** encoding.
3. The `eval()` function executes the decoded output in the PDF reader's context.

### B. Payload Decryption

The obfuscated string was decoded using a Python-based Base85 decryptor:

<img width="582" height="211" alt="image" src="https://github.com/user-attachments/assets/94d8d30e-c175-4996-bb96-b75d5abb1f29" />

The resulting payload revealed the flag/malware signature: **`hack10{M4l1ci0s_PDF}`**.
