<img width="613" height="727" alt="image" src="https://github.com/user-attachments/assets/29393a66-b3a7-4f84-b9fb-3dab47aca5a0" />

### **Reconnaissance & Protocol Analysis**

The first step was identifying the "Storm." We used the protocol hierarchy to see where the bulk of the data was hiding.

<img width="1155" height="672" alt="image" src="https://github.com/user-attachments/assets/a1082922-c48b-449b-8da4-2270d3a39cd8" />

**Observation:** We saw a massive amount of **UDP** traffic (the interference) and a consistent stream of **OSPF** (the routing breach).

### **Payload Investigation (The Decoy)**

We initially suspected the flag might be hidden in the raw data of the UDP packets, which appeared to be encoded with Shikata Ga Nai (SGN).

**Command to extract the "Storm" payload:**

<img width="997" height="102" alt="image" src="https://github.com/user-attachments/assets/b8f06ce8-db0f-4dd7-adf8-bb543adcd1e1" />

**Observation:** This led to "ghost" strings and scrambled data, confirming that the UDP flood was a distraction—the "Storm of Interference."

### **Analyzing the "Silent Pattern" (OSPF)**

Following the hint about "visualizing the form," we shifted focus to the OSPF protocol fields, specifically the **Advertising Router IDs**.

**Command to inspect the OSPF Router IDs:**

<img width="797" height="677" alt="image" src="https://github.com/user-attachments/assets/3ff44ca8-53fc-499e-b66e-fcd9f10aa629" />

**Observation:** We noticed hundreds of random IPs, but a specific set of internal IPs (`192.168.1.x`) appeared in a sequence. We suspected the flag was hidden in the last octet of these IDs.

### **The "Martial Artist" Reconstruction**

We realized the Source IP of the OSPF packets was the **index** (the form), and the Router ID was the **strike** (the data). We had to sort by Source IP to get the flag in the correct order.

**The Final Winning Command:**

<img width="1152" height="131" alt="image" src="https://github.com/user-attachments/assets/8e0a0ea4-0b69-4a29-8f7b-cce6365d8636" />

After cutting through the OSPF noise and following the martial artist's form, the pattern finally revealed:

> **`UMCS{ls4_t0p0logy_m4st3r_doj0}`**
>
