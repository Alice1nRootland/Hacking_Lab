# PH-2026-00029 — Suspected Malaysian E-Wallet Reward Phishing

> **Case status:** Taken down (as recorded by Rectifyq PhishHunt on 15 October 2026, 20:01:52, platform-displayed time)  
> **Case ID:** PH-2026-00029  
> **Platform:** Rectifyq PhishHunt  
> **Sharing designation shown on case:** TLP:CLEAR  
> **Investigation activity:** PAP:AMBER — passive and authorized analysis  
> **Investigation period:** 9–15 October 2026

## Executive summary

A reward-themed webpage at `hxxps://kongsi[.]apptng[.]xyz/Rayamacam2.my15` displayed branding associated with Touch 'n Go eWallet on an unrelated domain. A previously captured urlscan.io screenshot showed gift/envelope imagery and a **“Buka Sekarang”** (“Open Now”) call to action. These characteristics raised suspicion of brand impersonation and a possible phishing lure. The visible screenshot did **not** independently demonstrate a credential collection form, successful credential theft, or a downstream payload.

The case was submitted to Rectifyq PhishHunt on 11 October 2026 and subsequently validated through the platform's community workflow. Abuse reports were recorded for Cloudflare and Netcraft; a separate PhishDestroy report was recorded by another hunter. Cloudflare advised that the reported URLs were no longer accessible, and Netcraft later changed the primary URL's classification from **processing** to **unavailable**. PhishHunt's automated Pendeta monitoring subsequently recorded consecutive dead checks and moved the case to **Taken down** on **15 October 2026 at 20:01:52**.

**Outcome:** PhishHunt-confirmed takedown status and corroborating inaccessibility observations. The responsible remediation actor, root cause of inaccessibility, and permanence of the outage are **not established**.

## Investigation scope and handling

- **Primary investigated URL:** `hxxps://kongsi[.]apptng[.]xyz/Rayamacam2.my15`
- **Additional URL associated with the same PhishHunt case:** `hxxps://kongsi[.]apptng[.]xyz/Rayamacam2.my11` — recorded by another hunter; its content was **not independently verified** in this investigation.
- **Suspected impersonated service:** Touch 'n Go eWallet (Malaysia).
- **Observed lure:** Reward-claim themed landing page.
- **Method:** Passive review of existing screenshot and platform intelligence, infrastructure enrichment, authorized abuse reporting, and monitoring of external service results.
- **Safety:** No instruction or requirement to browse the suspected phishing page directly; do not interact with its calls to action.

The case header displayed **TLP:CLEAR**, permitting public sharing under that designation. Before publication, recheck the current case-level sharing permissions and redact personal information, credentials, nonpublic submissions, and restricted intelligence. PAP:AMBER governs investigative actions and is not a substitute for publication permission.

## Detection and validation

The primary URL was found during hunting using an existing [urlscan.io result](https://urlscan.io/result/01a11f6a-987d-714a-a48f-b3eba5854757/). Its captured page displayed Touch 'n Go eWallet-associated branding, gift graphics, and a “Buka Sekarang” button on `kongsi[.]apptng[.]xyz`, a domain outside the expected brand identity.

These observations support an **analyst assessment of suspected phishing/brand impersonation**. PhishHunt subsequently marked the case **Validated** through its voting process. Platform validation is not the same as an independently observed credential-harvesting transaction.

## Technical analysis and infrastructure

| Attribute | Observed finding | Interpretation / caveat |
| --- | --- | --- |
| Domain | `apptng[.]xyz` | Suspicious brand-adjacent naming; not proof of malicious ownership by itself |
| Host | `kongsi[.]apptng[.]xyz` | Host of the primary submitted URL |
| A records observed during investigation | `104[.]21[.]53[.]74`, `172[.]67[.]210[.]97` | Cloudflare reverse-proxy addresses, **not confirmed origin-server IPs** |
| Network | AS13335, CLOUDFLARENET | Identifies visible edge network, not necessarily the hosting origin |
| Nameservers | `algin.ns.cloudflare.com`, `selah.ns.cloudflare.com` | Cloudflare DNS infrastructure observed during enrichment |
| Certificate evidence | First certificate observed 23 September 2026; associated names included `apptng[.]xyz`, `kongsi[.]apptng[.]xyz`, `suppor[.]apptng[.]xyz`, `refunds[.]apptng[.]xyz` | Certificate naming alone does not establish all hosts were active or malicious |
| Registrar / origin | Not reliably identified | Registrar RDAP lookup returned HTTP 403 during investigation |

See [IOCs.md](IOCs.md) for indicator context and handling notes.

## Correlation and related observations

PhishHunt listed two URLs on the site. The second path, `/Rayamacam2.my11`, was contributed by another hunter; no independent screenshot or page-content confirmation was available to this investigation. A similar path, `/Rayamacam2.my`, appeared in another case (PH-2026-00014). Path resemblance suggests a lead for further investigation, **not a proven common operator or campaign**.

## Reporting and provider responses

| Recipient / channel | Recorded action | Result supported by evidence |
| --- | --- | --- |
| Cloudflare | Abuse report submitted 14 Oct 2026, approximately 11:52 MYT; report ID `c95bd385b7f821c8` | Acknowledgment received; follow-up stated reported URLs were no longer accessible. Cloudflare noted it was not the origin host. This does **not** identify the takedown actor. |
| Netcraft | Primary URL submitted 14 Oct 2026, 12:00:16 | Classification log changed **processing → unavailable** at 15:15:09 on 14 Oct; submission last updated 15 Oct, 03:55:37. Not a malicious-site classification. |
| PhishDestroy | Email report recorded by another PhishHunt hunter | **Sent — awaiting reference** at last review; external confirmation not established. |
| Google Safe Browsing | No report submitted during this investigation | Further reporting was deferred after multiple services reported inaccessibility. |

[Netcraft submission record](https://report.netcraft.com/submission/VIKlitvDAsOz3BCZdc7YzI5ZXhDahAQP) · [PhishHunt case](https://phishhunt.rectifyq.com/cases/PH-2026-00029)

## Takedown verification and limitations

PhishHunt's Pendeta checks reported the site **dead**, with **four consecutive dead results** visible in the Recheck tab on 15 October 2026. The first dead result was displayed as **14 October 2026, 20:01:18**. The platform's policy required two dead results at least 24 hours apart before marking a case down. The Overview subsequently showed all four stages completed and:

> Taken down 15/10/2026, 20:01:52

The case also displayed **dead** in its latest liveness summary. The saved screenshot documents the platform outcome.

<img width="1146" height="342" alt="phishhunt-takedown-confirmed" src="https://github.com/user-attachments/assets/905b3893-1525-4daf-8c11-5c0c831f6213" />

**Important distinction:** “Taken down” is the **platform's confirmed case status** based on its monitoring. The available evidence does not establish whether a registrar, origin host, Cloudflare, site operator, or another party caused the page to become inaccessible. Availability could change; the platform indicates the case may reopen if the page returns.

## Evidence and references

1. [PhishHunt case PH-2026-00029](https://phishhunt.rectifyq.com/cases/PH-2026-00029) — validation, reporting, Pendeta monitoring, and takedown status (some content may require membership).
2. [urlscan.io screenshot and scan](https://urlscan.io/result/01a11f6a-987d-714a-a48f-b3eba5854757/) — historical landing-page observation.
3. [Netcraft submission details](https://report.netcraft.com/submission/VIKlitvDAsOz3BCZdc7YzI5ZXhDahAQP) — classification log and unavailability result.
4. [PhishHunt takedown screenshot](evidence/phishhunt-takedown-confirmed.png) — locally retained evidence of the final platform status.
5. Cloudflare abuse acknowledgment and follow-up — reviewed during investigation; private email headers and personal details are **not published**. Report ID is included only as a tracking reference.

See [TIMELINE.md](TIMELINE.md) for the chronological record.

## Mitigation, monitoring, and conclusion

As of the final reviewed platform state on **15 October 2026**, PH-2026-00029 was marked **Taken down**. No further Tier-3 verification credit or duplicate abuse report was needed. If the page resurfaces, reassess it using authorized methods, update the case's Recheck tab with firsthand evidence as required, and document any change in status.

This case illustrates why analysts should separate **suspicious visual evidence**, **community validation**, **provider accessibility observations**, and **formal platform takedown status**. Multiple independent observations can strengthen confidence that a page is inaccessible without proving who caused the disruption.

---

*Defanged indicators are used for safe public documentation. This report describes observed evidence and the PhishHunt platform's case status; it does not claim independent attribution, confirmed credential theft, or a provider-caused takedown.*
