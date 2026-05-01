<img width="700" height="641" alt="image" src="https://github.com/user-attachments/assets/0af96205-173b-4eec-ae73-fb355bbb23a2" />

*“In this challenge, we analyze a packet capture (*`MarketDump.pcapng`*) to identify how an attacker accessed and exfiltrated sensitive customer data. Our goal: find the targeted card number and reconstruct the attack path.”*

### **Initial Filtering**

- **Command:**
    
    `tshark -r MarketDump.pcapng -Y "http.request" -T fields -e http.request.`
    

<img width="965" height="357" alt="image" src="https://github.com/user-attachments/assets/cac9cabd-af33-4a63-8a35-ee762626a74d" />

### **Identifying the Sensitive File**

`http.request.uri contains "costumers.sql”`

this command i use to filter in wireshark 

<img width="1519" height="214" alt="image" src="https://github.com/user-attachments/assets/1cb713db-7a65-465f-b579-5739aa01e520" />

and found our target at first line

**To follow the full TCP stream**:

- Right-click the filtered packet → *Follow* → *TCP Stream*

<img width="767" height="852" alt="image" src="https://github.com/user-attachments/assets/116f1e6c-d1a2-4308-871d-12c2e72d6207" />

then i saved it as dump.txt 

```php
grep -E '[A-Za-z0-9+/]{20,}={0,2}' dump.txt
```

i use this command to grep any encryption 

<img width="846" height="95" alt="image" src="https://github.com/user-attachments/assets/2cbc75f9-c055-4550-87c0-45399375032c" />

Decode it

<img width="858" height="83" alt="image" src="https://github.com/user-attachments/assets/2b5a5341-9600-4534-a258-bb23ef34d4bb" />

```php
HTB{DonTRuNAsRoOt!MESsEdUpMarket}                                                                                                       
```

we found the flag!
