# PH-2026-00019 — Indicators and Observables

> **PRIVATE — publication permission unresolved.** Defanged for safe reading. These are investigative indicators, **not all confirmed malicious IOCs**. Do not visit suspicious URLs directly.

| Type | Defanged value | Basis | Confidence / limitation |
|---|---|---|---|
| Suspected URL | `hxxps://touncngo[.]reward5[.]my[.]id/` | PhishHunt case, Lookyloo, Netcraft | High confidence observed; malicious function not fully proven |
| Hostname | `touncngo[.]reward5[.]my[.]id` | Lookyloo TLS subject and capture | High confidence historical |
| Base domain | `reward5[.]my[.]id` | Case infrastructure | High confidence associated; don't assume all paths/subdomains malicious |
| IPv4 | `202[.]73[.]25[.]122` | Lookyloo HAR, PhishHunt enrichment | High confidence historical resolution; shared hosting possible |
| ASN | `AS141892` | PhishHunt enrichment | Context only; not inherently malicious |
| Nameserver | `ns1[.]hypercloudhost[.]com` | Platform enrichment | Context only |
| Nameserver | `ns2[.]hypercloudhost[.]com` | Platform enrichment | Context only |
| Reverse hostname | `srv101[.]hypercloudhost[.]com` | Platform enrichment | Context only |
| Relative URL path | `login.php` | Captured HTML hyperlink | Link confirmed; endpoint behavior unknown |

## Technical artifacts

- HTTP response in existing capture: **200**, `content-type: text/html`, server **LiteSpeed**.
- TLS 1.3; certificate subject `touncngo.reward5.my.id`, issuer field `YR1`, valid 2026-10-04 to 2027-01-02 (historical capture).
- Reward script: `Math.random()` with bounds 5.00–99.99 and `toFixed(2)`; amount presented with `RM` in markup.
- Page title: “Touch 'n Go Rewards”; visible button “Buka Sekarang”; next-stage link “Lihat Butiran” to `login.php`.

## Do not overinterpret

- A valid TLS certificate does **not** establish site trustworthiness.
- A `login.php` link alone does **not** prove a credential-harvesting form.
- A shared IP/ASN does **not** identify a threat actor.
- Netcraft's **no threats found** verdict does **not** establish benignness; it is a documented provider classification.
- No verified exfiltration destination, credential submission, OTP request, or QR distribution mechanism is included in the evidence set.

## Reference captures

- Lookyloo: https://lookyloo.circl.lu/tree/a2bb8615-b509-42ad-9d11-44a4f669cc54
- urlscan: https://urlscan.io/result/01a11f05-cb93-72f8-8259-5695d0c4e929/
