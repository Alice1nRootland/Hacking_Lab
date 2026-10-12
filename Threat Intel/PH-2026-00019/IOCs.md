# IOCs — PH-2026-00019

> Public-review draft. Defanged indicators; treat as historical observations.

| Type | Value | Evidence / limitation |
|---|---|---|
| URL | `hxxps://touncngo[.]reward5[.]my[.]id/` | Rectifyq public feed |
| URL | `hxxps://reward5[.]my[.]id/` | Rectifyq public feed |
| Domain | `reward5[.]my[.]id` | Rectifyq public feed |
| IP | `202[.]73[.]25[.]122` | Historical Lookyloo HAR; not an exclusive malicious IP |
| ASN | `AS141892` | Rectifyq public feed; shared infrastructure possible |
| Relative path | `login.php` | Captured HTML only; destination not visited or verified |
| Target alias | Slate E-Wallet | Public feed's anonymized organization label |

**Classification:** PhishHunt `reported`, `tlp:clear`; Netcraft `no threats found` at recorded update. No confirmed takedown. Do not automatically block an entire ASN or shared IP based on this case alone.

Source: https://github.com/rectifyq/phishhunt-feed/blob/main/feeds/latest.csv
