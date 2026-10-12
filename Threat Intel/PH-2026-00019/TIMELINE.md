# PH-2026-00019 — Investigation Timeline

> **PRIVATE — not for public distribution.** Dates reflect source displays or prior investigator review. Time zone is unknown unless explicitly stated. Distinguish event dates from later review dates.

| Date / time | Event | Evidence / status |
|---|---|---|
| 2026-09-28 | Domain registration date recorded by PhishHunt enrichment | Historical registration metadata; independent registrar verification not reproduced here |
| 2026-10-04 | TLS certificate validity begins (Lookyloo record) | Captured certificate metadata |
| 2026-10-09 04:55:47 GMT | Lookyloo captured HTML response header `date` | Historical GET 200, LiteSpeed; does not establish present liveness |
| 2026-10-09 | PhishHunt case investigated and validated by analyst vote; stage later advanced to Reported | Platform case screenshot reviewed; exact validation time not preserved |
| 2026-10-09 23:33 MYT (earlier Gmail review) | Hosting abuse email sent to `abuse@as.net.id` | Email screenshot preserved, but visible screenshot does **not** show timestamp or full recipient address; no external ticket verified |
| 2026-10-09 23:38:31 (Netcraft display) | Netcraft submission created | Submission page; provider time zone unspecified |
| 2026-10-09 23:44:28 (Netcraft log display) | Netcraft URL changed from processing to **no threats** | Provider classification log shown in earlier review |
| 2026-10-12 17:10 (Netcraft display) | Issue with submission reported | Provider page displays this date/time; **do not infer local time or reconcile with later observation** |
| 2026-10-12 23:45:04 (Netcraft display) | Last update on Netcraft submission | Still displayed “no threats found” when reviewed |
| 2026-10-13 (investigator review) | Registrar ResellerCamp form displayed successful submission message | Screenshot shown during conversation; original screenshot not available in this package; no ticket number |
| 2026-10-13 (investigator review) | Static analysis of existing Lookyloo rendered HTML identified random reward and `login.php` hyperlink | Original HTML and screenshots 03–04 preserved |
| 2026-10-13 (investigator review) | Netcraft issue confirmation observed and explanation reviewed | Screenshot shown during conversation; original screenshot not available in this package |
| 2026-10-13 (investigator review) | Evidence collection reviewed; PhishHunt screenshot showed **Reported** | Original screenshot 01 not available in this package; sharing authorization unresolved |

## Pending follow-ups

- **Hosting:** check for genuine acknowledgement/ticket and any remediation response.
- **Registrar:** check for acknowledgement/ticket; do not fabricate a reference or resubmit to create one.
- **Netcraft:** check whether classification changed; do not infer blocklisting from issue submission.
- **PhishHunt:** verify liveness and takedown only via authorized platform methods consistent with PAP.
- **Disclosure:** confirm effective TLP label and platform rules before public GitHub or LinkedIn publication.
- **Evidence:** add the missing original screenshots 01, 06, 07 if locally available; preserve provenance.
