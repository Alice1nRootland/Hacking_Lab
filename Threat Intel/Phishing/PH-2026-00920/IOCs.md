# PH-2026-00920 — Indicators and correlation leads

> Historic indicators, **not** proof of current maliciousness at each related host. Defanged URLs and domain names below are intentionally non-clickable.

| Type | Value | Context / confidence |
|---|---|---|
| Investigated URL | `hxxps://touch-n-go14[.]ewallet-24[.]click/` | PhishHunt case PH-2026-00920; down 27 Oct 2026 |
| Registered domain | `ewallet-24[.]click` | Reported suspended by NameSilo |
| IPv4 A | `172[.]67[.]202[.]184` | Historical Cloudflare edge, shared infrastructure |
| IPv4 A | `104[.]21[.]85[.]55` | Historical Cloudflare edge, shared infrastructure |
| IPv6 AAAA | `2606:4700:3031::6815:5537` | Historical Cloudflare edge |
| IPv6 AAAA | `2606:4700:3030::ac43:cab8` | Historical Cloudflare edge |
| NS | `susan[.]ns[.]cloudflare[.]com` | Historical nameserver |
| NS | `lloyd[.]ns[.]cloudflare[.]com` | Historical nameserver |
| ASN | AS13335 | Cloudflare, not attacker attribution |
| Recorded kit-hash field | `ed266825df2ff85cc4f27593f50f15249848b8464712bb4371e9b7566b007f92` | Manually recorded in PhishHunt as `manual · urlscan`; **not verified as an archive hash** |

## Related domains — leads only

Certificate subject alternative names in historical enrichment included defanged names `money-paket[.]ewallet-24[.]click`, `touch-n-go27[.]ewallet-24[.]click`, `touch-n-go47[.]ewallet-24[.]click`, `touch-n-go13[.]ewallet-24[.]click`, and `touch-n-go5[.]ewallet-24[.]click`. SAN presence alone does not establish active hosting or malicious conduct by those hosts. A separate PhishHunt case PH-2026-00142 included `touch-n-go26[.]ewallet24[.]click` (**a different registered domain**) and a matching platform-recorded hash; shared actor attribution remains unproven.

## References

- https://urlscan.io/result/01a16cb8-fd34-74cb-92f0-06316a0310b4/
- https://urlscan.io/result/01a0605a-4499-715d-ab62-f325c1c039da/

**Caution:** Never use these indicators as the sole basis for blocking shared Cloudflare IPs. Confirm scope and current resolution first.
