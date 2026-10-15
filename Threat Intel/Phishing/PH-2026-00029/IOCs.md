# Indicators and Infrastructure — PH-2026-00029

> **Classification:** Investigative indicators for a suspected e-wallet reward-phishing case. Presence in this list does **not** mean every associated IP, certificate name, or infrastructure service is malicious.

## Primary and related URLs

| Indicator (defanged) | Type | Evidence / confidence |
| --- | --- | --- |
| `hxxps://kongsi[.]apptng[.]xyz/Rayamacam2.my15` | Primary URL | Captured in existing urlscan result; PhishHunt validated case; later marked down |
| `hxxps://kongsi[.]apptng[.]xyz/Rayamacam2.my11` | Additional case URL | Added by another hunter; page content not independently verified |
| `kongsi[.]apptng[.]xyz` | Hostname | Observed host of primary URL |
| `apptng[.]xyz` | Registered domain | Parent domain; infrastructure context |

## Network and DNS observations

| Indicator (defanged) | Type | Caveat |
| --- | --- | --- |
| `104[.]21[.]53[.]74` | IPv4 A record | Cloudflare edge address; not confirmed origin |
| `172[.]67[.]210[.]97` | IPv4 A record | Cloudflare edge address; not confirmed origin |
| `AS13335` | ASN | Cloudflare network, not attribution to an attacker |
| `algin.ns.cloudflare.com` | Nameserver | Shared service infrastructure |
| `selah.ns.cloudflare.com` | Nameserver | Shared service infrastructure |

**Avoid blanket blocking of Cloudflare IPs or AS13335:** these are shared service indicators and can host or proxy unrelated legitimate sites. Apply controls to the confirmed suspicious URL or hostname according to local policy and current evidence.

## Certificate and domain-name leads

The earliest certificate date visible during enrichment was **23 September 2026**. Observed names included:

- `apptng[.]xyz`
- `kongsi[.]apptng[.]xyz`
- `suppor[.]apptng[.]xyz`
- `refunds[.]apptng[.]xyz`

These are **investigative leads**, not separately validated phishing URLs. No claim is made that the other subdomains served phishing content.

## Related-case lead

PhishHunt case **PH-2026-00014** included a similarly named `/Rayamacam2.my` path. Shared naming alone is insufficient to attribute a common actor or campaign.

## Unknown or not established

- Origin-server IP and physical hosting location
- Reliable registrar attribution from the attempted RDAP query
- Credential submission or exfiltration endpoint
- Malware payload, kit hash, or credential-theft confirmation
- Common operator behind similar paths
- Party responsible for making the site inaccessible

## Supporting records

- [Historical urlscan result](https://urlscan.io/result/01a11f6a-987d-714a-a48f-b3eba5854757/)
- [PhishHunt case](https://phishhunt.rectifyq.com/cases/PH-2026-00029)
- [Netcraft report](https://report.netcraft.com/submission/VIKlitvDAsOz3BCZdc7YzI5ZXhDahAQP)

*Use defanged indicators in public reports. Do not open suspicious URLs directly in a personal browser.*
