<img width="701" height="641" alt="image" src="https://github.com/user-attachments/assets/957d6999-89df-4b62-9f17-c376c369be41" />

Connect to the docker 

<img width="1163" height="243" alt="image" src="https://github.com/user-attachments/assets/c6500c55-7766-4bd2-96c8-b7e64af590a4" />

check what files are given

<img width="1564" height="678" alt="image" src="https://github.com/user-attachments/assets/bf3d0875-e540-45f8-ba37-c61f1171a401" />

> *Which event log contains information about logon and logoff events? (for example: Setup)*
> 

<img width="1124" height="128" alt="image" src="https://github.com/user-attachments/assets/0462bdc5-7845-4b23-bab7-accdfd39f5d3" />

We focus on `Security.evtx` because Windows records logon/logoff/auth events in the **Security** event log
Answer : **Security**

> What is the event id for logs for a successful logon to a local computer? (for example: 1337)
> 

## Why Security.evtx?

Windows segregates event logs by type. The **Security** log stores authentication-related events (logon, logoff, account changes). Event IDs you should know:

- **4624** = successful logon
- **4625** = failed logon
- **4634** = logoff
- **4648**, **4672**, **4688** = related security events

So to find suspicious successful logons, search **4624** entries inside `Security.evtx`.

Answer : **4624**

> *Which is the default Active Directory authentication protocol? (for example: http)*
> 

┌──(kali㉿kali)-[~/Desktop/htb/Logs]
└─$ `sed -i '1d' Security.xml`

┌──(kali㉿kali)-[~/Desktop/htb/Logs]
└─$ `sed -i '1i <Events xmlns="http://schemas.microsoft.com/win/2004/08/events/event">' Security.xml
echo '</Events>' >> Security.xml`

┌──(kali㉿kali)-[~/Desktop/htb/Logs]
└─$ `xmlstarlet sel -N ev="http://schemas.microsoft.com/win/2004/08/events/event" \
-t \
-m '//ev:Event[ev:System/ev:EventID="4624"]' \
-v 'concat(ev:System/ev:TimeCreated/@SystemTime, " | ", ev:EventData/ev:Data[@Name="TargetUserName"], " | AuthPkg=", ev:EventData/ev:Data[@Name="AuthenticationPackageName"])' -n \
Security.xml`

**Explanation:**

- `N ev=...` registers the XML namespace used in EVTX-exported XML (required for XPath).
- `m` matches `Event` nodes whose `EventID` is `4624`.
- `v 'concat(...)'` prints a formatted line combining desired fields
    
<img width="1572" height="233" alt="image" src="https://github.com/user-attachments/assets/be44074c-33a2-4b59-9f36-e635f9b23df3" />
    

So if you search your `Security.evtx` for **4624 events** and then check the value of `AuthenticationPackageName`, you’ll often see **Kerberos** unless the system fell back to NTLM

## Why Kerberos is the answer

- Kerberos is faster and more secure (ticket-based, symmetric encryption).
- It supports mutual authentication (client ↔ server).
- It’s required for features like single sign-on (SSO).
- That’s why Microsoft made it the default.

> *Looking at all the logon events, what is the AuthPackage that stands out as different from all the rest? (for example: http)*
> 

## Look for the odd AuthenticationPackage

Most AD domain logons should show `Kerberos`. The challenge hint was a downgrade: network authentication not forced, so find where the logon used **NTLM** instead of Kerberos.

```bash
xmlstarlet sel -t \
  -m '//Event[System/EventID=4624]' \
  -v 'EventData/Data[@Name="AuthenticationPackageName"]' -n \
  Security.xml | sort | uniq -c
```

<img width="1571" height="197" alt="image" src="https://github.com/user-attachments/assets/2ee50f91-7e3c-45f0-b046-205743c48494" />

## Identify the suspicious one

- The **majority** will be `Kerberos` (the default for Active Directory).
- If see **NTLM** (or anything else, e.g. `MSV1_0`), that’s the **odd one out** and the answer.

Answer : **NTLM**

> *What is the timestamp of the suspicious login (yyyy-MM-ddTHH:mm:ss) UTC? (for example, 2021-10-10T08:23:12)*
> 

## Extract all successful logons (4624) with timestamp + user + IP + AuthPkg

```bash
xmlstarlet sel -t \
  -m '//Event[System/EventID=4624]' \
  -v 'concat(System/TimeCreated/@SystemTime, " | User=", EventData/Data[@Name="TargetUserName"], " | Ip=", EventData/Data[@Name="IpAddress"], " | AuthPkg=", EventData/Data[@Name="AuthenticationPackageName"])' -n \
  Security.xml
```

<img width="1577" height="579" alt="image" src="https://github.com/user-attachments/assets/1cb088fe-594a-427a-b591-dbaab8c78d80" />

Most NTLM events are for `vagrant` or `ANONYMOUS LOGON`. The one that stands out is the **Administrator** NTLM logon at:

**Answer: 2022-09-28T13:10:57 UTC**

Why this one:

- It’s the only NTLM 4624 entry for **Administrator** (others are `vagrant`/anonymous).
- A domain **Administrator** authenticating with **NTLM** (instead of Kerberos) is unusual and therefore suspicious.

## Why the Administrator NTLM entry is suspicious

- `Administrator` is a high-privilege account — any deviation is notable.
- AD default is **Kerberos**; seeing a domain **Administrator** authenticate with **NTLM** suggests a downgrade or fallback to an older protocol — possibly due to misconfiguration or an attack that forced NTLM.
- The challenge premise explicitly mentioned "network authentication is not forced," hinting NTLM usage.

So the event to pick is the NTLM 4624 for `Administrator`

## Final answer and flag

- **Event log:** `Security`
- **Event ID for successful logon:** `4624`
- **Default AD auth protocol:** `Kerberos`
- **AuthPackage that stands out:** `NTLM`
- **Suspicious timestamp (UTC):** `2022-09-28T13:10:57`
- **Flag:** `HTB{34sy_t0_d0_4nd_34asy_t0_d3t3ct}`
