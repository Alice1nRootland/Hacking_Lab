<img width="498" height="564" alt="image" src="https://github.com/user-attachments/assets/91123ad5-c5e9-4879-a40c-dcadba69efd2" />

## **Step 1: Analyzing the Binary**

1. Using **dnSpy**  we decompiled the binary.
2. Observed a function named `HashEmail(string email)`:

<img width="716" height="346" alt="image" src="https://github.com/user-attachments/assets/f49d2d1a-7dbd-46b8-bd14-af36fd2949ec" />

### **Key observations:**

- The binary uses **MD5** to hash emails.
- Comparison is done against a **hardcoded target hash**:

```
0d103375d4f99df6bc92a931aa8f48b1
```

- This is a **classic hash-matching challenge**, often solvable with a wordlist.

<img width="1296" height="722" alt="image" src="https://github.com/user-attachments/assets/abb05750-bc94-49a6-8b69-ee30302c2fde" />

## **Step 2: Identifying the Target Hash**

From the IL / decompiled code, we confirmed:

```
if (HashEmail(input) == "0d103375d4f99df6bc92a931aa8f48b1")
{
    Console.WriteLine("HACK10{…}");
}
```

<img width="1294" height="720" alt="image" src="https://github.com/user-attachments/assets/5cccd3d6-8963-42a0-aa7a-a1ec4ac41e35" />

## **Step 3: Preparing a Wordlist**

- A URL was provided with a list of potential email addresses:

```
https://appsecmy.com/d22646ad92dfaa334f9fa1c3579b4801.txt
```

- Download and process emails to standardize format (lowercase, strip spaces).
<img width="606" height="359" alt="image" src="https://github.com/user-attachments/assets/cbcc5987-65c7-4670-85cd-3d22ac2b028e" />

```
HACK10{wa00d6d88epd0z1x6gro@rediffmail.com}
```
