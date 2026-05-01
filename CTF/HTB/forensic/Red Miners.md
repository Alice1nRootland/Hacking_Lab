<img width="697" height="644" alt="image" src="https://github.com/user-attachments/assets/a6d3fa8f-0e9d-48ba-b78c-8551410024f1" />

I try to read as string first 

<img width="1655" height="720" alt="image" src="https://github.com/user-attachments/assets/4b335e08-b6ac-4048-8cc0-ee3e295eedf9" />

then i notice there is base64 so i try to deocde it 

<img width="985" height="505" alt="image" src="https://github.com/user-attachments/assets/4053d9e1-c1e5-457c-9351-ba0aa164e318" />

i conclude the flag is divide by part and each part is encoded with base64 

so try the powerful command instead 

```php
grep -Eo '[A-Za-z0-9+/=]{10,}' miner_installer.sh | sort | uniq | while read line; do
  echo "$line" | base64 -d 2>/dev/null && echo "---"
done
```

<img width="1525" height="337" alt="image" src="https://github.com/user-attachments/assets/5dcab0b6-eeaf-4601-a2f8-fb29d38eb8de" />

<img width="1477" height="113" alt="image" src="https://github.com/user-attachments/assets/adbe26a7-e489-46c6-a19c-95882db1861a" />

they i can se each divided part of the flag 

```php
HTB{m1n1ng_th31r_w4y_t0_m4rs_th3_r3d_pl4n3t}
```
