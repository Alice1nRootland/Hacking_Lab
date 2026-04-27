<img width="618" height="841" alt="image" src="https://github.com/user-attachments/assets/b307ee4d-29c6-4b82-a51e-add749ca604c" />

The hint "silence is only achieved when opposites collide" refers to **Phase Inversion**. In a stereo file, sounds that are perfectly centered are identical in the Left (L) and Right (R) channels. By subtracting one from the other, we cancel out the "Anthem" and reveal the hidden "Phantom" signal.
We used the following formula for destructive interference:

<img width="203" height="50" alt="image" src="https://github.com/user-attachments/assets/22a3524d-7cb0-4df8-992a-dbc0cf219fc3" />

<img width="805" height="560" alt="image" src="https://github.com/user-attachments/assets/e71d5526-eee0-492d-9c1e-a79ae1e1744d" />

### **Signal Transcription**

Listening to `Ghost_Amplified.wav` revealed a hidden voice speaking in **Morse Code**.

<img width="1460" height="961" alt="image" src="https://github.com/user-attachments/assets/3f667cd8-678c-4b63-acdf-ef166252112e" />

• **Translated Text:** `LUYKBBFZEJNHPKEXGNTOTHIUYCO`
****

### **Step C: Identifying the Key**

The "Father of the University" is **Tunku Abdul Rahman**, the first Chancellor of Universiti Malaya (UM). He was installed and took his oath on **June 16, 1962**. This gave us the context for the key. Testing his name as the key:

- **Key:** `TUNKU`

### **Step D: Decryption**

Using the **Vigenère Cipher** on CyberChef with the key `TUNKU`, the ciphertext `LUYKBBFZEJNHPKEXGNTOTHIUYCO` decrypted to:

> `SALAHILMUPUNCAKEMAJUANVKEJU`
> 

<img width="882" height="503" alt="image" src="https://github.com/user-attachments/assets/a8a1c83d-b15f-4834-9c30-e0005f128db0" />

flag: `UMCS{ILMU_PUNCA_KEMAJUAN}`
