# PH-2026-00920 — Investigation timeline

> Times shown in Malaysia time (MYT, UTC+08) where the original records made that clear. Netcraft's original timestamps are also given in UTC. No fabricated ticket IDs or provider responses.

| Date / time | Event | Evidence / qualification |
|---|---|---|
| 2026-06-10 | Registered domain `ewallet-24[.]click` created | Historical registrar enrichment |
| 2026-08-08 | Earliest certificate issuance recorded in enrichment | Historical CertSpotter-derived metadata |
| 2026-09-02 | Earlier urlscan capture showed title “A surprise Money Packet for you!” | [Historical scan](https://urlscan.io/result/01a0605a-4499-715d-ab62-f325c1c039da/) |
| 2026-10-23 13:22:57 (platform display) | PH-2026-00920 created by first submitter `pelagosintel` | PhishHunt Overview; not submitted by this investigator |
| 2026-10-24 | Newer historical scan recorded reward-themed landing page and Touch 'n Go eWallet branding | [urlscan result](https://urlscan.io/result/01a16cb8-fd34-74cb-92f0-06316a0310b4/) |
| Date not independently pinned down | Case validated via one PhishHunt vote of weight +3 | Platform validation, not confirmed credential theft |
| 2026-10-25 23:14–23:31 MYT (reporting session) | Cloudflare abuse report submitted; Report ID `5cc0134d1361cf01` | Confirmation email; exact filing minute not independently verified |
| 2026-10-25 23:18 MYT (email sent time) | Registrar report emailed to NameSilo | Gmail Sent correspondence; no ticket assigned |
| 2026-10-25 23:21:32 MYT / 15:21 UTC | Netcraft submission made | Submission ID `8e3mHxY3BEj4gs8JTw10srn95AhnqjSa` |
| 2026-10-25 23:40:03 MYT / 15:40 UTC | Netcraft automated classification changed from processing to **No threats found** | [Netcraft record](https://report.netcraft.com/submission/8e3mHxY3BEj4gs8JTw10srn95AhnqjSa) |
| 2026-10-25 23:45 MYT / 15:45 UTC | Netcraft misclassification review filed, citing historical capture and Cloudflare response | Netcraft acknowledgment on existing submission; revised outcome pending |
| 2026-10-25 (reporting session) | Google Safe Browsing submission successful | Official form completion; no classification confirmed |
| 2026-10-25 (reported via email) | Cloudflare confirmed access restriction and forwarding to website owner and relevant hosting provider; named Contabo GmbH | Trust & Safety response tied to Cloudflare report ID; provider-side restriction, not origin deletion |
| 2026-10-25 (after host identification) | Direct follow-up email sent to Contabo `abuse@contabo.de` | Investigator confirmation; no reply/ticket recorded |
| 2026-10-26 14:20 MYT | NameSilo Abuse Team replied: “The abusive domain(s) has been suspended.” | Provider email; no ticket reference supplied |
| 2026-10-26 20:02:55 (platform display) | First non-live Pendeta observation | DNS/RDAP tier-1 liveness |
| 2026-10-27 20:03:02 (platform display) | **PhishHunt marked case down; Taken down ✓** | NXDOMAIN; first dead result 26 Oct 20:02:55; later five dead results in a row |

## Reporting status at closure

Cloudflare: report ID exists; access restriction confirmed. NameSilo: reported suspension confirmed; ticket ID absent. Netcraft: review requested but original **No threats found** verdict remains recorded. Google Safe Browsing: submitted; blocking status unconfirmed. Contabo: direct email sent; response not available in the provided record.

**Causation:** The timing and acknowledgements do **not** establish which report caused the suspension.
