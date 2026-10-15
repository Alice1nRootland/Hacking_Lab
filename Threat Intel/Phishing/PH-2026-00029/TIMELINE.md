# Investigation Timeline — PH-2026-00029

> Dates and times are reproduced from the available records. Where the original service's timezone is not explicit, the time is shown as displayed rather than independently converted. Approximate times are identified as such.

| Date / time | Event | Evidence and interpretation |
| --- | --- | --- |
| **23 Sep 2026** | Earliest certificate date observed in enrichment | Certificate-history context; not proof of phishing start date |
| **9 Oct 2026** | Historical urlscan capture available | Screenshot showed reward-themed Touch 'n Go eWallet-associated branding and “Buka Sekarang” button on unrelated host |
| **11 Oct 2026, 00:59:23** | PhishHunt case created | Submitted by Cyber_Aliceee; case ID PH-2026-00029 |
| **Before reporting, date not independently recorded** | PhishHunt validation completed | Community workflow showed **Validated** |
| **14 Oct 2026, ~11:52 MYT** | Cloudflare abuse report submitted | Acknowledgment received; tracking ID `c95bd385b7f821c8` |
| **14 Oct 2026, shortly after acknowledgment** | Cloudflare follow-up received | Provider stated reported URLs were no longer accessible; not independent takedown attribution |
| **14 Oct 2026, 12:00:16** | Netcraft report submitted | [Submission record](https://report.netcraft.com/submission/VIKlitvDAsOz3BCZdc7YzI5ZXhDahAQP) |
| **14 Oct 2026, 15:15:09** | Netcraft classification changed | **processing → unavailable**, not a malicious verdict |
| **14 Oct 2026, 20:01:18** | First dead Pendeta result displayed | Start of observed dead-check sequence |
| **15 Oct 2026, 03:55:37** | Netcraft submission page last updated | Displayed one unavailable URL |
| **15 Oct 2026, earlier platform review** | PhishHunt Recheck showed dead | Four consecutive dead results; case still displayed Reported at that review |
| **15 Oct 2026, 20:01:52** | **PhishHunt marked case Taken down** | Final Overview showed Submitted ✓, Validated ✓, Reported ✓, Taken down ✓ |
| **15 Oct 2026, final review** | Takedown evidence saved | [Final status screenshot](evidence/phishhunt-takedown-confirmed.png) |

## Reporting status at final review

- **Cloudflare:** Report submitted, acknowledgment and inaccessibility follow-up received.
- **Netcraft:** Report submitted; primary URL marked unavailable.
- **PhishDestroy:** Report sent by another hunter; external reference still pending at last observation.
- **Google Safe Browsing:** Not submitted; deferred after corroborated inaccessibility.

## Final status and caveat

PhishHunt recorded the case as **Taken down** on 15 October 2026 at 20:01:52. This establishes the platform's outcome under its liveness-check rules; it does **not** establish which organization or mechanism caused the site to stop responding. Continue monitoring only if the case reopens or new evidence emerges.
