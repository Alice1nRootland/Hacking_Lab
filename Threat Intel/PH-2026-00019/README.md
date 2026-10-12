# PH-2026-00019 — E-Wallet Reward-to-Login Investigation

> **Public Threat Intelligence Case Study**
> Case source: Rectifyq PhishHunt public TLP:CLEAR feed
> Case state: **Reported** · Reviewed: 13 October 2026
> Target alias: **Slate E-Wallet** · Takedown: **Not confirmed**


## Executive summary

This case concerns a suspicious reward-themed website listed in Rectifyq PhishHunt's public TLP:CLEAR feed. An existing Lookyloo capture shows an e-wallet-themed gift/envelope landing page. Static inspection of the saved rendered HTML found a JavaScript-generated reward amount (RM5.00–RM99.99) and a **“Lihat Butiran”** (View Details) link targeting the relative path `login.php`.

**Analyst assessment:** The observed design and reward-to-login progression are consistent with potentially deceptive social engineering. **Unknown:** The contents of `login.php` were not examined; credential/OTP collection, data exfiltration, and attacker identity are not confirmed. The case's **Reported** status is not a takedown verdict.

## Scope and methodology

Passive review of already captured Lookyloo content, saved HTML, and published PhishHunt feed fields. No new contact with the suspicious website was required. Provider verdicts are recorded as observed rather than treated as definitive proof.

## Evidence 1 — Reward-themed landing page

<img width="1920" height="1080" alt="02-lookyloo-landing png" src="https://github.com/user-attachments/assets/27c69da8-d796-4d31-bd4c-57043b9f1490" />

*Figure 1. Existing Lookyloo screenshot; the image illustrates the lure but does not establish credential collection.*

## Evidence 2 — Client-side random reward

<img width="683" height="152" alt="04-html-random-reward" src="https://github.com/user-attachments/assets/16e8291f-7de6-485f-9657-14d9c5f89444" />

*Figure 2. `generateRandomAmount()` uses `Math.random()` with minimum 5.00 and maximum 99.99. The displayed amount is not a verified account balance.*

The opening button changes the displayed section and assigns the generated amount to the page. This is observed in the static HTML, not inferred from live interaction.

## Evidence 3 — Second-stage login link

<img width="547" height="63" alt="03-html-login-link" src="https://github.com/user-attachments/assets/6dfaa713-abff-4fbb-925a-ddf9cdc6c6e1" />

*Figure 3. The “Lihat Butiran” anchor has `href="login.php"`. The target page's behavior is unknown.*

## Infrastructure and published IOCs

The following fields are recorded in Rectifyq's public feed for **two URLs belonging to PH-2026-00019**:

| Field | Public feed value |
|---|---|
| URL 1 | `hxxps://touncngo[.]reward5[.]my[.]id/` |
| URL 2 | `hxxps://reward5[.]my[.]id/` |
| Registrable domain | `reward5[.]my[.]id` |
| Case state | `reported` |
| Target alias | `Slate E-Wallet` |
| Sector / vector | `ewallet` / `qr` |
| Registrar | `PT JC Indonesia (IANA 1)` |
| ASN / country | `AS141892` / `ID` |
| TLP | `tlp:clear` |
| Takedown timestamp | Not populated in feed |

The `qr` vector is a **platform metadata field**, not independent proof that the investigator observed QR distribution. Historical Lookyloo HAR information additionally recorded `202[.]73[.]25[.]122`, HTTP 200, TLS 1.3, and LiteSpeed. Infrastructure ownership is **not** attribution of the operator.

## Evidence 4 — External classification disagreement

<img width="1457" height="502" alt="05-netcraft-classification" src="https://github.com/user-attachments/assets/92371d6f-e3c2-44cb-a291-128cd1b137fc" />

*Figure 4. Netcraft's recorded classification was “no threats found” with displayed last update 12 October 2026 23:45:04. This is a vendor verdict, not a safety guarantee.*

The existing Netcraft submission also displayed a recorded issue report for reassessment. **No changed verdict, block, or takedown was confirmed.**

## Reporting and outcome

Abuse reports were made to infrastructure contacts and the registrar, and a Netcraft classification issue was recorded. These are investigator actions supported by **private records not reproduced here**. No external abuse ticket number, provider remediation, or successful takedown is claimed.

## Limitations and lessons learned

- A visually convincing landing page alone does not prove credential theft.
- Client-side reward generation and a `login.php` link are concrete, reproducible observations from captured source.
- Platform validation, vendor classification, and site availability are separate findings.
- Do not infer common operators from shared hosting or network indicators.
- Preserve screenshots and original capture evidence privately; public excerpts should not expose account data or restricted case materials.

## References

- [Rectifyq PhishHunt public feed — latest.csv](https://github.com/rectifyq/phishhunt-feed/blob/main/feeds/latest.csv) (case `PH-2026-00019`, two records)
- [Lookyloo existing capture](https://lookyloo.circl.lu/tree/a2bb8615-b509-42ad-9d11-44a4f669cc54)
- [urlscan existing result](https://urlscan.io/result/01a11f05-cb93-72f8-8259-5695d0c4e929/)
- [Netcraft submission](https://report.netcraft.com/submission/qD83d0i5iJVarIYVSHOMYMCk57HtqdWu)

*This report is an evidence-based investigation summary, not a claim of confirmed compromise, attribution, or takedown.*
