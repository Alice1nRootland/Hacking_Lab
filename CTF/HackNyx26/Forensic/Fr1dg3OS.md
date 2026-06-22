<img width="627" height="861" alt="image" src="https://github.com/user-attachments/assets/2f362d37-fb0c-4e35-b931-15fcfd02c5ce" />

#### Initial Triaging & Keyboard Cipher Breakdown

The challenge attachment provides an archive named `Fr1dg3OS_evidence.7z`. Extracting the archive yields two massive files:

<img width="587" height="478" alt="image" src="https://github.com/user-attachments/assets/d86f93f5-6aca-437f-854b-44294b0f2c0b" />


The challenge description provides a string of symbols: `&#@^*$@)`. mapping these symbols back to their shifted numerical counterparts on a standard US QWERTY keyboard layout reveals a hidden offset or parameter:
• **`&`** →7, **`#`** → 3, **`@`** → 2, **`^`** →  6, **`*`** →  8, **`$`** →  4, **`@`** →  2, **`)`** →  0
• **Translated Value:** `73268420`

#### Volatile Memory Carving

Using standard string processing on the RAM snapshot (`Fr1dg3OS.raw`) targeting the suspicious exfiltration time window (**03:13**), we unearth the internal system configurations and daemon scripts:

<img width="1107" height="672" alt="image" src="https://github.com/user-attachments/assets/35bd2281-04ce-49c2-a9e2-33a27464bbf6" />


#### Leaked Target Logic:

The memory architecture yields an automated configuration execution sequence matching the runtime initialization script:

```jsx
#!/bin/bash
LOG="/opt/fridgeos/logs/error.log"
VAULT="/opt/fridgeos/vault/service_backup.luks"
MAPPER="coldvault"
MOUNTPOINT="/mnt/coldvault"

if [ -n "$COLDVAULT_RUNTIME_TOKEN" ]; then
    echo -n "$COLDVAULT_RUNTIME_TOKEN" | cryptsetup luksOpen "$VAULT" "$MAPPER" - 2>/dev/null
    mount "/dev/mapper/$MAPPER" "$MOUNTPOINT" 2>/dev/null
    shred -u /etc/fridgeos/runtime.env
fi
```

Further environmental string mining extracts the plain text variables mapped directly from the target system environment initialization sequence:

<img width="630" height="186" alt="image" src="https://github.com/user-attachments/assets/d9875c50-d576-44d6-b0bf-2ae1f4dbb619" />


*Note: The `AI_SOLVER_NOTE` is flagged as an anti-analysis honeypot indicator and skipped.*

#### Disk Partitioning & LVM Management

Inspecting the disk image configuration (`Fr1dg3OS.img`) via `fdisk` maps out a standard GPT structure ending with a Linux system partition layer:

<img width="567" height="226" alt="image" src="https://github.com/user-attachments/assets/59a10b1b-c4b8-4e98-8c2d-ed2611fecd2c" />


Mounting partition 3 directly fails because it is wrapped inside an **LVM2 Logical Volume container**. To access the underlying filesystem root, we mount the raw image to a system loop device, dynamically install the `lvm2` system binaries, scan the metadata fields, and activate the volume group:

<img width="1017" height="470" alt="image" src="https://github.com/user-attachments/assets/bdcfeda9-4417-4a8e-bce4-ee7c6dbe14fc" />


With the target volume structure online, the active root path maps cleanly to the localized loop filesystem boundary:

```jsx
sudo mount /dev/mapper/ubuntu--vg-ubuntu--lv /mnt/fridge_root
```

#### Container Decryption & SQLite Carving

Following the runtime paths identified in Phase 2, we locate the secure encrypted vendor cache container file inside the newly mapped directory structure at `/opt/fridgeos/vault/service_backup.luks`.

We pipe the recovered volatile memory token to pass the encryption layer validation sequence, map it to an unsealed crypto block device node, and safely mount the data tables:

<img width="773" height="271" alt="image" src="https://github.com/user-attachments/assets/c4797172-e0e8-41df-9447-f1a0d4e8ebd3" />


Extracting the schema properties of the main SQL database engine found within `/telemetry/fridge_metrics.db` yields table initializations for metadata blocks (`evidence_blob`), but checking active index paths returns zero valid entries.

Knowing from logs that rows were deleted but `PRAGMA secure_delete=OFF` was globally declared, the underlying engine has flagged deleted storage spaces as unallocated free blocks rather than zeroing out the structural registers.

By dumping raw page values via hex data carving directly past file termination tags, the un-indexed orphaned text fragments are exposed in the database slack space:

<img width="642" height="797" alt="image" src="https://github.com/user-attachments/assets/70276139-4eca-4104-8035-cd4749421887" />


#### Reconstructing the Flag

Isolating the raw text array strings from the database free blocks reveals the final target structure:

<img width="578" height="62" alt="image" src="https://github.com/user-attachments/assets/7c987870-0434-41c7-8754-d1e22f6e2e91" />

we get the flag!
