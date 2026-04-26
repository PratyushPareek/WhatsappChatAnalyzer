# WAChatAnalysis — Parsing & Format Notes

## WhatsApp Chat Export Format

### Message Line Format

Two formats are supported (auto-detected from the first 50 lines):

**Format A** (12-hour, dash separator):
```
M/D/YY, H:MM AM/PM - Sender: Message content
```
- Date: `M/D/YY` (no leading zeros, 2-digit year)
- Time: `H:MM AM/PM` (12-hour, no leading zero)
- Separator: ` - ` (space-dash-space) between timestamp and rest
- Sender/message separator: `: ` (colon-space)

**Format B** (24-hour, square brackets):
```
[DD/MM/YY, HH:MM:SS] Sender: Message content
```
- Date: `DD/MM/YY` (may have leading zeros, 2-digit year)
- Time: `HH:MM:SS` (24-hour with seconds)
- Wrapped in `[...]`; some lines prefixed with U+200E (left-to-right mark)
- Sender/message separator: `: ` (colon-space)

### Regex

Format A:
```python
r'^(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}[\s\u202f][APap][Mm])\s-\s'
```

Format B:
```python
r'^\u200e?\[(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}:\d{2})\]\s'
```

### Encoding Quirk
- **Newer messages (2026+)**: narrow no-break space `\u202F` before AM/PM (Format A)
- **Older messages (2019–2023)**: regular space before AM/PM (Format A)
- **Format B**: may prefix lines with `\u200E` (left-to-right mark), stripped during parsing
- Parser handles both via `[\s\u202f]` in Format A regex

### Multi-line Messages
Lines not matching the date regex are continuation of the previous message:
```
9/25/23, 7:31 PM - Alice: Hey
Are you coming tomorrow?
```

### System Messages
No `: ` after the sender — no sender at all:
```
9/4/19, 1:20 AM - Messages and calls are end-to-end encrypted. ...
```

---

## Special Message Types

### Media — Three Formats
1. `<Media omitted>` → `media_type = unknown` (not exported)
   - **Multiline media**: If a media message has continuation lines (e.g., `<Media omitted>` followed by `Footloose`), the parser detects media on the **first line only** and drops continuation lines. This prevents media messages from leaking into text stats.
2. `FILENAME (file attached)` → classified by:
   - **Prefix**: `STK-` → sticker, `IMG-` → image, `VID-` → video, `PTT-`/`AUD-` → audio, `DOC-` → document
   - **Extension**: `.vcf` → contact, `.pdf` → pdf
   - **Fallback**: `unknown`
3. `X omitted` (Format B) → `sticker omitted`, `image omitted`, `video omitted`, `audio omitted`, `document omitted`, `GIF omitted`, `Contact card omitted`

### Deleted Messages
- `This message was deleted` (other person deleted)
- `You deleted this message` (exporter deleted)

### Missed Calls
- `Missed voice call`
- `Missed video call`

---

## Date Format Detection
Parser auto-detects US (`M/D/YY`) vs international (`D/M/YY`) by scanning first 500 lines:
- If first field ever exceeds 12 → `DMY`
- If second field ever exceeds 12 → `MDY`
- Ambiguous → defaults to `MDY`
- Can be overridden in `config.yaml` via `date_format: "MDY"` or `"DMY"`

---

## Stop Words
Configured in `config.yaml`. Default list includes ~250 words:
- **English**: common function words (the, a, is, was, etc.), contractions, pronouns
- **Hinglish**: Hindi transliterated words (hai, ka, ki, ke, ko, toh, nahi, etc.)
- **YAML gotcha**: `yes`, `no`, `on`, `off` must be quoted (`"yes"`) to avoid YAML boolean parsing. The settings loader also applies `str()` coercion as a safety net.
