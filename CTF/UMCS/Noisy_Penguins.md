### Step 1: Initial Container Analysis

The challenge provides an `.mkv` video file. Matroska (`.mkv`) files are container formats capable of holding multiple video, audio, subtitle, and attachment streams. To see what was inside the container, we ran an initial inspection using `mkvinfo` and `exiftool`

<img width="843" height="737" alt="image" src="https://github.com/user-attachments/assets/e2bdff0a-aed1-496f-932f-1cf979e9d24f" />

**Observation:** The output revealed a hidden file attached within the MKV container:

<img width="396" height="102" alt="image" src="https://github.com/user-attachments/assets/2a730192-199e-4bc2-8361-d9a5fec2d340" />

### Step 2: Extracting the Hidden Payload

Knowing there was a 46MB `PINGU.mp4` file embedded in the original MKV, we used `ffmpeg` to dump the attachment into our working directory.

<img width="1280" height="730" alt="image" src="https://github.com/user-attachments/assets/7b2bcc6d-b27d-4212-b8a7-ba21cfc40373" />

This successfully extracted `PINGU.mp4`.

### Step 3: Analyzing the Extracted Video

Upon inspecting the newly extracted `PINGU.mp4` file, we needed to check for any hidden audio frequencies, metadata, or subtitle tracks. Running a probe on the new file revealed a suspicious subtitle track (`tx3g` format).

We extracted the subtitle stream to a readable `.srt` format:

<img width="1287" height="755" alt="image" src="https://github.com/user-attachments/assets/8412749a-4cee-4466-9e46-1885e577cfef" />

### Step 4: Inspecting the Subtitles

Reading the extracted `subs.srt` file revealed several suspicious, seemingly random strings mapped to different timestamps in the video:

<img width="413" height="346" alt="image" src="https://github.com/user-attachments/assets/79716486-0268-423c-bfce-9d4d56e8e5b8" />

**Step 5: Decoding the Base64 Strings**

<img width="470" height="77" alt="image" src="https://github.com/user-attachments/assets/666bf2b3-9daa-40da-b581-90d8f88132eb" />

flag: 

```sql
UMCS{ascii_p3nGu1n_n00t}
```

l
