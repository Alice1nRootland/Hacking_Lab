# PH-2026-00019 — E-Wallet Reward-to-Login Investigation

> **Public Threat Intelligence Case Study**  
> Case source: Rectifyq PhishHunt public TLP:CLEAR feed  
> Case state: **Reported** · Updated: 14 October 2026  
> Target alias: **Slate E-Wallet** · Provider-reported suspension: **14 October 2026**  
> PhishHunt-confirmed takedown: **Not confirmed**

## Executive summary

This investigation concerns a suspicious e-wallet reward-themed website tracked under Rectifyq PhishHunt case **PH-2026-00019**.

An existing Lookyloo capture showed a gift/envelope-themed landing page. Static examination of the captured HTML identified JavaScript-generated reward amounts between RM5.00 and RM99.99 and a **“Lihat Butiran”** (View Details) link pointing to `login.php`.

These observations are consistent with potentially deceptive social engineering. However, the destination page was not examined, so credential collection, OTP theft, data exfiltration and attacker identity remain unconfirmed.

**Update — 14 October 2026:** ResellerCamp responded to the phishing abuse report stating that the domain had been suspended. A separate observation showed a HyperCloudHost suspension notice replacing the previously captured reward page.

Despite this development, PhishHunt's Pendeta monitoring continued to report the site as `live`, with zero consecutive dead checks. The case remained **Reported**.

The evidence supports a **provider-reported suspension and observed content replacement**, not a confirmed permanent takedown.

## Investigation scope and methodology

The investigation used passive and previously collected evidence, including:

- Rectifyq PhishHunt public feed information.
- An existing Lookyloo capture.
- Static examination of saved rendered HTML.
- Historical network and hosting indicators.
- Netcraft classification information.
- Abuse-reporting correspondence.
- An investigator-supplied hosting suspension screenshot.

No additional interaction with the suspicious site's login functionality was performed.

## Evidence 1 — Reward-themed landing page

<img width="1920" height="1080" alt="Lookyloo capture of the reward-themed landing page" src="https://github.com/user-attachments/assets/27c69da8-d796-4d31-bd4c-57043b9f1490" />

*Figure 1. Historical Lookyloo screenshot showing the reward-themed landing page. Its appearance does not independently establish credential collection.*

## Evidence 2 — Client-side random reward

<img width="683" height="152" alt="JavaScript reward generation evidence" src="https://github.com/user-attachments/assets/16e8291f-7de6-485f-9657-14d9c5f89444" />

*Figure 2. The captured JavaScript function `generateRandomAmount()` uses `Math.random()` to generate amounts between RM5.00 and RM99.99.*

The opening button changes the displayed page section and assigns the generated reward amount. This behavior was identified through static HTML analysis, not live interaction.

The generated value is not evidence of a genuine account balance or legitimate reward.

## Evidence 3 — Second-stage login link

<img width="547" height="63" alt="HTML login.php link evidence" src="https://github.com/user-attachments/assets/6dfaa713-abff-4fbb-925a-ddf9cdc6c6e1" />

*Figure 3. The “Lihat Butiran” anchor contains `href="login.php"`.*

The destination's content and functionality were not examined. Therefore, credential harvesting and OTP collection are not independently confirmed.

## Infrastructure and indicators

The following fields were published in Rectifyq's TLP:CLEAR feed for two URLs associated with PH-2026-00019.

| Field | Value |
|---|---|
| URL 1 | `hxxps://touncngo[.]reward5[.]my[.]id/` |
| URL 2 | `hxxps://reward5[.]my[.]id/` |
| Domain | `reward5[.]my[.]id` |
| Target alias | Slate E-Wallet |
| Sector | E-wallet |
| Reported vector | QR |
| Registrar | PT JC Indonesia (IANA 1) |
| Historical IP | `202[.]73[.]25[.]122` |
| ASN | AS141892 |
| Country | Indonesia |
| Case status | Reported |
| TLP | CLEAR |

The QR vector is PhishHunt metadata; its use in distributing this particular page was not independently verified.

Historical Lookyloo evidence additionally recorded HTTP 200, TLS 1.3 and LiteSpeed.

Infrastructure ownership and shared hosting do not establish attacker identity.

## Evidence 4 — External classification disagreement

<img width="1457" height="502" alt="Netcraft historical classification evidence" src="https://github.com/user-attachments/assets/92371d6f-e3c2-44cb-a291-128cd1b137fc" />

*Figure 4. Netcraft's recorded classification was “no threats found,” with a displayed last update of 12 October 2026 at 23:45:04.*

An issue requesting classification reassessment was also recorded.

A vendor's `no threats found` classification is not proof of safety. No revised Netcraft verdict was independently confirmed in the evidence reviewed.

## Evidence 5 — Registrar-reported suspension

On **14 October 2026**, ResellerCamp replied to the phishing abuse report.

An initial response at **09:25** acknowledged receipt and indicated that the report was being investigated.

A subsequent response at **10:03** stated:

> Domain telah ditangguhkan

English translation: **The domain has been suspended.**

This is a direct statement from the registrar's abuse correspondence, rather than an automated reputation verdict.

The original emails are preserved privately. Only a redacted evidence excerpt should be shared publicly.

<img width="1512" height="532" alt="image" src="https://github.com/user-attachments/assets/80da8174-2376-456c-9098-6ba25f86af31" />

*Figure 5. Redacted provider correspondence reporting domain suspension on 14 October 2026. Personal contact details and unrelated correspondence are excluded.*

**Evidence limitation:** The provider response supports the reported suspension but does not independently establish why the domain was suspended, whether all related services were affected, or whether the action is permanent.

## Evidence 6 — Hosting suspension notice

A separately supplied screenshot showed a HyperCloudHost suspension notice displaying:

> Layanan Hosting Dinonaktifkan

English translation: **Hosting service disabled.**

The notice appeared instead of the reward-themed landing page previously recorded by Lookyloo.

<img width="1054" height="698" alt="Screenshot from 2026-10-14 09-03-07" src="https://github.com/user-attachments/assets/2be10de2-9770-4921-81c2-513585e29b7d" />

*Figure 6. Investigator-supplied screenshot showing the hosting suspension notice. The observation supports a change in served content, not proof of permanent domain removal.*

The suspension notice does not independently establish the administrative or technical reason for the suspension.

## PhishHunt liveness and takedown verification

Following the registrar response, a Tier-3 recheck was submitted to PhishHunt recording the changed page content.

A subsequent platform view continued to show:

| Field | Observed platform status |
|---|---|
| Case stage | Reported |
| Pendeta liveness | Live |
| Consecutive dead checks | 0 |
| First dead result | None recorded |
| Taken-down stage | Not reached |

A discussion update was posted under the investigator's PhishHunt account documenting the provider response and observed suspension page.

PhishHunt indicates that two dead results at least 24 hours apart are required for its automated takedown transition.

**Assessment:** The reported phishing lure appears disrupted in the supplied observation, but a PhishHunt-confirmed takedown has not been established.

## Abuse reporting and investigation outcome

The investigation included reports to the registrar, hosting infrastructure contact and Netcraft.

The following outcomes are supported by the available evidence:

- ResellerCamp acknowledged the abuse report.
- ResellerCamp subsequently reported domain suspension.
- A hosting suspension notice was observed.
- A Netcraft classification issue was submitted.
- A PhishHunt Tier-3 recheck and discussion update were submitted.
- PhishHunt continued to classify the case as Reported and the site as live at the latest supplied review.

No external abuse ticket number is claimed where one has not been supplied.

Private email headers, contact details and correspondence are not included in the public report.

## Limitations and lessons learned

- A convincing phishing-style landing page does not alone prove credential theft.
- Client-side reward generation and a `login.php` link are observable technical indicators.
- Provider suspension statements and automated liveness verdicts measure different things.
- A hosting suspension notice may still be served by a responsive web server.
- Shared infrastructure does not establish common operator attribution.
- A suspension may be temporary; continued verification is required.
- Preserve original evidence privately and publish only authorized, sanitized excerpts.

## References

- [Rectifyq PhishHunt public feed](https://github.com/rectifyq/phishhunt-feed/blob/main/feeds/latest.csv) — PH-2026-00019
- [Lookyloo historical capture](https://lookyloo.circl.lu/tree/a2bb8615-b509-42ad-9d11-44a4f669cc54)
- [urlscan historical result](https://urlscan.io/result/01a11f05-cb93-72f8-8259-5695d0c4e929/)
- [Netcraft submission](https://report.netcraft.com/submission/qD83d0i5iJVarIYVSHOMYMCk57HtqdWu)
- ResellerCamp abuse correspondence, 14 October 2026 — private original retained
- Investigator-supplied hosting suspension screenshot, 14 October 2026

---

*This report documents a defensive threat intelligence investigation. Provider-reported suspension and observed content replacement are supported by the available evidence; permanent takedown, attacker attribution and credential compromise are not independently confirmed.*
