<img width="699" height="643" alt="image" src="https://github.com/user-attachments/assets/6b1a5a26-9015-4fbb-8d5e-519cc370492c" />

## Challenge Description

We are given a small Node.js project containing a Discord bot (`bot.js`) and a `config.json`. The challenge hints that sensitive information might be hidden in the repository.

---

## Initial Enumeration

Start by listing the files:

```bash
ls -la
```

<img width="1267" height="167" alt="image" src="https://github.com/user-attachments/assets/7c5221a7-ddb2-4446-a7f9-b170edec3261" />

The `.git/` folder immediately stands out. This means we can inspect the repository history for secrets.

## Inspecting `config.json`

The current `config.json` contains:

<img width="1347" height="193" alt="image" src="https://github.com/user-attachments/assets/570a98f6-b585-46dc-ab0a-d072291c8fb5" />

Decoding the base64 in `username`:

<img width="1599" height="90" alt="image" src="https://github.com/user-attachments/assets/298e6264-5024-47ad-9122-246cc083f309" />

This tells us the username field is a **decoy**. We need to dig deeper.

## Exploring Git History

Check commits that touched `config.json`:

```bash
git log --oneline config.json
```

<img width="1513" height="103" alt="image" src="https://github.com/user-attachments/assets/d2e78b47-564d-4560-9b19-8cbf8ab3ff4b" />

The first commit (`335d6cf`) is suspicious because it likely contains the original token.

## Recovering the Old Token

Show `config.json` at commit `335d6cf`:

```bash
git show 335d6cf:config.json
```

<img width="1593" height="217" alt="image" src="https://github.com/user-attachments/assets/fc4bd20b-469a-4ed8-88f2-a2f3fcc38a74" />

## Decoding the Token

Decode with base64:

```bash
echo 'SFRCe3YzcnNpMG5fYzBudHIwbF9hbV9JX3JpZ2h0P30=' | base64 -d
```

<img width="1237" height="89" alt="image" src="https://github.com/user-attachments/assets/e7c17601-885d-4aa2-9814-b5d15a89bd39" />

`HTB{v3rsi0n_c0ntr0l_am_I_right?}`

That’s the flag.
