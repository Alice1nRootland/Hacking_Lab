<img width="705" height="644" alt="image" src="https://github.com/user-attachments/assets/17c84e3f-c498-4891-bf44-cdc883ef63f3" />

<img width="901" height="248" alt="image" src="https://github.com/user-attachments/assets/5224dcb6-8c69-4cf3-938a-190430b28d05" />

> What is the name of the OpenWRT backup file accessible over FTP?
> 

I try log in through ftp as anonymous and check the file 

<img width="920" height="461" alt="image" src="https://github.com/user-attachments/assets/df5c7bdb-8600-4950-81a3-dadef005246e" />

the answer is **backup-OpenWrt-2023-07-26.tar**

> Whats the WiFi password for SSID OpenWRT?
> 

after donwload the backup i read the 

### Extracting the WiFi Password (PSK)

Run:

bash

`cat ./etc/config/wireless`

<img width="920" height="586" alt="image" src="https://github.com/user-attachments/assets/3bd6e8c6-efd8-4b6c-98fd-cb982c9cebbf" />

The value of `option key` is your **WiFi password** — in this case, 
**VeRyUniUqWiFIPasswrd1**

> Which user reused the WiFi password on thier local account?
> 

### Identify the Reused Account

To find which user reused this password on their local account:

1. **Check** `/etc/passwd` **for usernames**
    
    bash
    
    `cat ./etc/passwd`
    
    Look for non-system users like:
    

<img width="913" height="222" alt="image" src="https://github.com/user-attachments/assets/0e13df0c-d033-43b5-9713-f45502a21296" />

> Submit the flag located in the netadmin user's home directory.
> 

then i proceed to use the username to login by SSH and with the password given here the step how i get the user flag

 `ssh [netadmin@10.129.229.90](mailto:netadmin@10.129.229.90)`

<img width="922" height="202" alt="image" src="https://github.com/user-attachments/assets/743b01e9-38b2-4bdd-ae0d-6d7ead6fa72d" />

```php
059c6ba78937964b0b7150e831769806
```

> Which interface is being used for monitoring?
> 

### **Network Interface Enumeration**

- Checked all network interfaces using `ifconfig` and `iw dev`.
- Observed multiple interfaces, including `mon0` in **monitor mode**:

<img width="924" height="598" alt="image" src="https://github.com/user-attachments/assets/591576d6-8e3c-4d45-8aaa-f690a507327e" />

- Other interfaces:
    - `wlan0` – AP (192.168.1.1)
    - `wlan1` – managed client (192.168.1.23)
    - `wlan2` – managed
- **Monitoring interface used:** `mon0`

> What is the WPA password for the network on the mon0 interface?
> 

### **WPA Password Recovery with Reaver**

- Used `reaver` to attack WPS on the AP:
    
    ```bash
    reaver -i mon0 -b 02:00:00:00:00:00 -vv
    ```
    
- Reaver successfully cracked the WPS PIN and retrieved the WPA PSK:

<img width="919" height="489" alt="image" src="https://github.com/user-attachments/assets/996d2c97-6712-4ddc-952a-1e5967851242" />

WPA PSK: WhatIsRealAnDWhAtIsNot51121!
AP SSID: OpenWrt
WPA password for network on mon0: **WhatIsRealAnDWhAtIsNot51121!**

### **Accessing Root Flag**

- Switched to root using the recovered password:
    
    ```bash
    su -
    ls
    cat root.txt
    ```
    
- Navigated to root folder and read the flag:

<img width="919" height="132" alt="image" src="https://github.com/user-attachments/assets/c7a02311-5def-4900-9340-d7515fc08232" />

```php
740732ca0cae1238bf60cd0754d1d5ec
```
