# PH-2026-00019 — Suspected Malaysian E-Wallet Reward Phishing

> **PRIVATE INVESTIGATION RECORD — NOT APPROVED FOR PUBLIC RELEASE**  
> Platform: Rectifyq PhishHunt · Case: PH-2026-00019 · Last documentation review: 13 October 2026  
> Platform case stage at screenshot: **Reported** (Submitted ✓, Validated ✓, Taken down not marked).  
> Case header displays `tlp:clear` and `PAP:AMBER` with adjacent `?` help icons. An earlier platform footer was described as `TLP:GREEN`; **effective sharing authorization remains unresolved**. Do not publish case-specific screenshots or indicators until confirmed.

## Executive summary

An existing Lookyloo capture of `hxxps://touncngo[.]reward5[.]my[.]id/` displays a page branded as “Touch 'n Go Rewards” with a yellow “Buka Sekarang” button. The captured rendered HTML contains JavaScript that produces a random amount between RM5.00 and RM99.99 and reveals a “Lihat Butiran” hyperlink with the relative destination `login.php`. These **observed** elements support an **analyst assessment** of a suspicious reward-to-login social-engineering flow and possible e-wallet brand impersonation. The contents of `login.php` were **not captured or examined**. Credential/OTP harvesting, exfiltration, and actor identity are **not established**.

PhishHunt recorded validation and the case stage **Reported**; that is a platform finding, not independent proof of credential theft. The existing Netcraft submission showed **“no threats found”** as of its displayed last update, 12 October 2026 23:45:04. Netcraft also displayed an issue report for review, but no revised verdict or block was evidenced. Successful takedown is **not confirmed**.

## Investigation scope and handling

- Passive review of existing Lookyloo capture, its saved rendered HTML, previously available urlscan evidence, PhishHunt case details, and abuse-reporting records.
- No live visit to the suspected website or its `login.php` endpoint was made for this report.
- TLP/PAP constraints apply; preserve original captures and provider correspondence privately. Never include private reporter data or unauthorized screenshots in public output.
- Dates below are recorded as displayed by their sources. **Provider time zones are not established**, and Netcraft's displayed issue date is not assumed to be the local submission date.

## Observed technical evidence

### Landing page / impersonation indicators

The saved Lookyloo screenshot depicts a blue gift/envelope interface, a Touch 'n Go-style logo, the title “Touch 'n Go Rewards,” and the “Buka Sekarang” button. This supports an impersonation concern; no authorization by the legitimate brand has been established. See `evidence/02-lookyloo-landing.png`.

### Random reward mechanism

The captured HTML implements `generateRandomAmount()` with `min = 5.00`, `max = 99.99`, and `Math.random()`; clicking `openBtn` replaces `saldoAmount` and changes which page section is visible. This amount is client-generated, **not a verified wallet balance**. See `evidence/04-html-random-reward.png` and the preserved source file.

### Second-stage link

The captured HTML includes `<a href="login.php" class="btn btn-yellow">Lihat Butiran</a>`. Because this is a **relative path**, it refers to a page under the captured site's URL context, but its response and behavior remain unknown. No claim of credential collection or data exfiltration is made. See `evidence/03-html-login-link.png`.

### Existing Lookyloo capture observations

The captured GET request returned **HTTP 200**, `text/html`, via **LiteSpeed**, with **TLS 1.3** and a certificate whose subject was `touncngo.reward5.my.id`; issuer field `YR1`, valid 2026-10-04 through 2027-01-02. HAR IP: `202.73.25.122`. These describe the **historical capture**, not present liveness or legitimacy. Existing capture: https://lookyloo.circl.lu/tree/a2bb8615-b509-42ad-9d11-44a4f669cc54

## Infrastructure findings

| Field | Recorded observation | Caveat |
|---|---|---|
| Host | `touncngo[.]reward5[.]my[.]id` | Suspected URL host |
| Base domain | `reward5[.]my[.]id` | Scope of associated case infrastructure |
| IP | `202[.]73[.]25[.]122` | Historical HAR / platform enrichment |
| ASN | `AS141892` | Platform enrichment |
| Network | IDNIC-SENGKED-AS-ID — CV Andhika Pratama Sanggoro | Network ownership is not actor attribution |
| Country | Indonesia | Hosting/infrastructure geography, not actor location |
| Registrar | PT JC Indonesia / ResellerCamp | From platform enrichment |
| Domain registration date | 2026-09-28 | From platform enrichment |
| Nameservers | `ns1[.]hypercloudhost[.]com`, `ns2[.]hypercloudhost[.]com` | From prior platform enrichment |
| Reverse hostname | `srv101[.]hypercloudhost[.]com` | From prior platform enrichment |
| Web server | LiteSpeed | Observed in Lookyloo HTTP response |

## Correlation and attribution limits

PhishHunt grouped this case within a “Slate E-Wallet” cluster (three cases sharing an IP). **Shared infrastructure is not evidence of common operator, coordinated campaign, or confirmed attribution.** No attribution conclusion is drawn.

## Reporting and external verdicts

| Channel | Observed action/status | What remains unknown |
|---|---|---|
| PhishHunt | Case shows Submitted ✓, Validated ✓, **Reported** | No confirmed takedown; current liveness requires authorized recheck |
| Hosting abuse | Email addressed to `abuse@as.net.id` sent (earlier Gmail review: 9 Oct 2026) | No external acknowledgement or ticket reference verified |
| Registrar | ResellerCamp form displayed “Terima Kasih, Laporan Abuse berhasil dikirim.” (13 Oct review) | No external ticket reference or remediation confirmed |
| Netcraft | Initial report submitted 9 Oct 2026; URL displayed **no threats found**; issue-report confirmation visible | No revised classification or blocking confirmed |

**Netcraft issue timestamp note:** Submission page displayed “An issue with this submission was reported at 17:10 on 12/10/2026.” Preserve that exact displayed timestamp; do not reconcile it by assumption with the date on which the investigator observed the page.

The hosting report email described QR-code distribution, but **independent evidence of QR-based distribution was not preserved**. Treat it as an unverified statement in the sent report.

## Evidence inventory

See `evidence/INDEX.md`. Original screenshots 01, 06, and 07 were shown during the investigation but are **not present in this exported working package**; their absence is explicit. The other five images and original HTML text are preserved in the package. Do not replace missing evidence with reconstructions.

## Evidence and references

- Lookyloo capture: https://lookyloo.circl.lu/tree/a2bb8615-b509-42ad-9d11-44a4f669cc54
- urlscan result: https://urlscan.io/result/01a11f05-cb93-72f8-8259-5695d0c4e929/
- Netcraft submission: https://report.netcraft.com/submission/qD83d0i5iJVarIYVSHOMYMCk57HtqdWu
- PhishHunt case: PH-2026-00019 (private platform record)

## Mitigation, takedown, and monitoring

**Takedown not confirmed.** PhishHunt's earlier “live · probed 4h ago” is a time-relative historical platform observation, not current availability. Check provider replies, external classification changes, and permitted liveness mechanisms; do not browse the suspected site directly. Do not resubmit duplicate abuse reports. If an external ticket arrives, record its actual identifier and source.

## Conclusion and lessons learned

The preserved static HTML adds meaningful evidence beyond the landing screenshot: a browser-generated reward and an explicit link to `login.php`. These observations support further provider review while **stopping short of unverified claims** about credential theft, actor attribution, or successful remediation. Preserve exact vendor verdicts, timestamps, source files, and uncertainty. Confirm TLP authorization before preparing any public GitHub or LinkedIn version.
