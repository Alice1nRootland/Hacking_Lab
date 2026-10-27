# PH-2026-00920 — E-Wallet Reward-Themed Phishing Investigation

> **Documentation status:** Public case-study draft; case-specific disclosure permission for platform records remains subject to PhishHunt sharing controls.  
> **Platform:** Rectifyq PhishHunt · **Investigator:** Cyber_Aliceee  
> **Case lifecycle:** Down — PhishHunt confirmed 27 October 2026, 20:03:02 (platform-displayed time).  
> **Observed URL (defanged):** `hxxps://touch-n-go14[.]ewallet-24[.]click/`

## Executive summary

PhishHunt case **PH-2026-00920** concerned a reward-themed page bearing Touch 'n Go eWallet branding. Historical urlscan captures displayed the title **“A surprise Money Packet for you!”**, a reward-themed visual, and a **“Buka Sekarang”** button. A browser console warning indicated a password input was present, but the investigation did **not** confirm credential submission, data exfiltration, or victim impact.

The case was validated through a PhishHunt member vote (weight +3), not through a completed platform AI verdict. Cloudflare Trust & Safety subsequently confirmed that it **restricted access to the reported URL** and forwarded the complaint to the site owner and hosting provider. NameSilo Abuse Team later stated that the reported abusive domain had **been suspended**. PhishHunt independently marked the case **down on 27 October 2026 at 20:03:02**, citing DNS/RDAP tier-1 checks returning **NXDOMAIN**, with the first dead result at **26 October 2026, 20:02:55**.

Netcraft's automated analysis classified the URL as **“No threats found”** on 25 October 2026. An evidence-based classification review was submitted later that day; a revised verdict has not been observed. This disagreement is preserved rather than silently resolved.

**Outcome:** Provider-confirmed domain suspension and PhishHunt-confirmed down status. No specific provider or investigator report is claimed as the proven cause of the outcome.

## Scope and methodology

The investigation used PhishHunt case records, historic urlscan results, passive domain/DNS/certificate enrichment, and actual abuse-provider replies. The suspicious URL was not opened directly on an investigator's personal computer, and no login, OTP, or other suspected collection flow was tested.

Sources were classified as (1) platform records, (2) independent passive captures, (3) provider correspondence, and (4) analyst assessment. Provider correspondence is retained privately. The public document includes only the minimal provider-response facts needed to substantiate the reported outcome.

## Visual and technical evidence

- **24 October 2026 urlscan capture:** [01a16cb8-fd34-74cb-92f0-06316a0310b4](https://urlscan.io/result/01a16cb8-fd34-74cb-92f0-06316a0310b4/) — historical observed reward-themed landing page.
- **2 September 2026 urlscan capture:** [01a0605a-4499-715d-ab62-f325c1c039da](https://urlscan.io/result/01a0605a-4499-715d-ab62-f325c1c039da/) — earlier capture with a matching page title.
- The October capture logged **14 HTTP GET requests**: 13 HTTP 200 responses and one HTTP 404 for `flags.webp`. No credential POST was observed in the reviewed request list. This does not establish that no collection behavior exists under other conditions.
- Browser developer tools emitted `[DOM] Password field is not contained in a form`. This supports the presence of a password input, **not** completed credential theft.
- JavaScript names such as `formatPhone`, `PHONE_GLOBAL`, `CURRENT_STEP`, and `gotoStep` suggest a staged phone-related interface; the underlying behavior was not fully verified.
- The redirect panel displayed a chain count, but detailed redirect destinations were not available in the recorded evidence. No destination is asserted.

### Figure 1 — Historical phishing landing page

![Historical urlscan capture of the reward-themed landing page](https://github.com/user-attachments/assets/9b316c38-bbb1-49c3-ace5-17c2d00028ab)

*Figure 1. urlscan capture from 24 October 2026 showing the reward-themed page, brand imagery, and the title “A surprise Money Packet for you!”. This historical capture does not prove credential exfiltration.*

## Infrastructure findings

| Attribute | Historical finding | Qualification |
|---|---|---|
| Registered domain | `ewallet-24[.]click` | Defanged |
| Registrar | NameSilo, LLC | PhishHunt enrichment |
| Registration | 10 June 2026 | Historic registration data |
| A records | `172[.]67[.]202[.]184`, `104[.]21[.]85[.]55` | Cloudflare edge addresses, not origin identity |
| AAAA records | `2606:4700:3031::6815:5537`, `2606:4700:3030::ac43:cab8` | Historical enrichment |
| NS | `susan[.]ns[.]cloudflare[.]com`, `lloyd[.]ns[.]cloudflare[.]com` | Historical enrichment |
| ASN | AS13335 (Cloudflare) | CDN attribution only |
| Origin host | Contabo GmbH, DE | Identified by Cloudflare abuse response; not independently resolved from origin IP |
| Certificates | Google Trust Services / Let's Encrypt | Historical CertSpotter-derived enrichment |
| Earliest recorded certificate | 8 August 2026 | Historical enrichment |

PhishHunt linked this case to **“Slate E-Wallet · same kit”** (two-case suspected cluster). The related-case recorded kit-hash match and overlaps in infrastructure are **correlation leads**, not proof of a shared operator. The SHA-256-looking string in [IOCs.md](IOCs.md) was manually recorded with source `urlscan`, and was **not independently verified as the hash of a recovered phishing-kit archive**.

## Abuse reporting and provider responses

| Party | Activity / result | Evidence status |
|---|---|---|
| Cloudflare | Phishing report submitted; ID `5cc0134d1361cf01`. Trust & Safety confirmed access restriction and forwarding to website owner and hosting provider; identified Contabo. | Provider-confirmed email |
| NameSilo | Email report sent 25 October; Abuse Team replied 26 October 2026, 14:20 MYT that the abusive domain(s) had been suspended. No ticket number supplied. | Provider-confirmed email |
| Netcraft | Submission `8e3mHxY3BEj4gs8JTw10srn95AhnqjSa`; automated **No threats found**, 25 October 2026, 15:40 UTC. Misclassification review recorded 15:45 UTC. | Public submission record; no revised verdict confirmed |
| Google Safe Browsing | Official form indicated successful submission; no ticket or confirmed block classification. | Submission confirmation |
| Contabo | Direct follow-up abuse email sent after Cloudflare identified it as hosting provider; no acknowledgement or ticket yet recorded. | Investigator-sent email |

### NameSilo suspension confirmation — private evidence

**Provider correspondence retained privately.** NameSilo confirmed by email on 26 October 2026 that the reported abusive domain had been suspended; the original message is withheld from this public case study to avoid exposing private correspondence.


### Figure 2 — Netcraft classification disagreement

![Netcraft automated classification showing no threats found](https://github.com/user-attachments/assets/d32dea8a-57df-48c8-bf1f-a9ebd9673712)

*Figure 2. Netcraft's automated “No threats found” verdict. A reconsideration request was subsequently recorded; no revised classification has been confirmed.*

PhishHunt's Report tab counted **four** reports; the direct Contabo email was documented separately and must not be represented as a fifth platform-recorded entry. Cloudflare's access restriction was **not** equivalent to registrar suspension, and the Netcraft classification was **not** a confirmed block.

## Takedown and monitoring

PhishHunt Pendeta's tier-1 DNS/RDAP monitoring first recorded non-live status on **26 October 2026 at 20:02:55**, later showing five consecutive dead checks. On **27 October 2026 at 20:03:02**, the platform changed the lifecycle to **`down`** and marked **Taken down ✓**, with cause **NXDOMAIN**. Its stated rule requires two dead probes separated by at least 24 hours. The site can later reappear; a new verified observation would require reassessment.

The available evidence establishes the observed down state and provider-reported actions, not perpetual unavailability or exclusive responsibility for the result.

### Figure 3 — PhishHunt takedown confirmation

![PhishHunt case displaying down status and completed takedown milestone](https://github.com/user-attachments/assets/9d2c8cd0-549c-4181-89e9-ce3c213bc0fc)

*Figure 3. PhishHunt case header showing `down` and the completed “Taken down” milestone on 27 October 2026. The Recheck tab independently records NXDOMAIN as the reason for the down state.*

## Conclusions and lessons learned

1. Historical passive captures are valuable when a site changes or becomes unreachable before other scanners inspect it.
2. A password-input warning and branded reward lure are notable, but they do not alone prove credential harvesting or victim losses.
3. CDN network addresses should not be mistaken for an origin server or attacker attribution.
4. Automated intelligence verdicts can conflict: record the original Netcraft **No threats found** outcome alongside the review request.
5. Distinguish **provider-restricted access**, **registrar-reported suspension**, and **PhishHunt-verified down state**.
6. Preserve provider correspondence privately and publish only redacted, authorized evidence.

## References and related files

- PhishHunt case ID: `PH-2026-00920` (platform case record; access and sharing controls apply)
- [October urlscan capture](https://urlscan.io/result/01a16cb8-fd34-74cb-92f0-06316a0310b4/)
- [September urlscan capture](https://urlscan.io/result/01a0605a-4499-715d-ab62-f325c1c039da/)
- [Netcraft submission and classification](https://report.netcraft.com/submission/8e3mHxY3BEj4gs8JTw10srn95AhnqjSa)
- [IOCs.md](IOCs.md) · [TIMELINE.md](TIMELINE.md)

> **Sharing note:** The PhishHunt case header displayed `tlp:clear` and `PAP:AMBER` when reviewed. The publication of this summary is not a claim of independent authorization for all case attachments or private correspondence. Provider emails and restricted records are excluded; recheck case-specific sharing controls before further redistribution.
