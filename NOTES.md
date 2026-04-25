# WAChatAnalysis — Format & Parsing Notes

## Source File
- **File**: `muskan-pratyush.txt`
- **Lines**: ~47,051
- **Participants**: Pratyush, Muskan
- **Date range**: Sep 4, 2019 → Apr 23, 2026 (~6.5 years)

## Message Line Format
```
M/D/YY, H:MM AM/PM - Sender: Message content
```
- Date: `M/D/YY` (month without leading zero, day without leading zero, 2-digit year)
- Time: `H:MM AM/PM` (12-hour, no leading zero on hour)
- Separator between date and sender: ` - ` (space-dash-space)
- Separator between sender and message: `: ` (colon-space)

### Encoding Quirk (Important!)
- **Newer messages (2026)** have a Unicode narrow no-break space (`U+202F`) before AM/PM
  - Renders as `â€¯` in some terminals (UTF-8 misinterpretation)
  - Example: `4/22/26, 1:27â€¯PM` = `4/22/26, 1:27\u202FPM`
- **Older messages (2019–2023)** use a regular space before AM/PM
  - Example: `9/4/19, 1:20 AM`
- **Parser must handle BOTH** regular space and `\u202F` before AM/PM

## Multi-line Messages
- Continuation lines do NOT start with a date pattern
- Example:
  ```
  9/25/23, 7:31 PM - Pratyush: Haan
  But merse to dur hi hoega kahin bhi
  ```
- Parser should accumulate continuation lines into the previous message

## System Messages (no sender)
```
9/4/19, 1:20 AM - Messages and calls are end-to-end encrypted. Only people in this chat can read, listen to, or share them. *Learn more*
```
- Format: `DATE - System message text` (no colon after the text before message)
- These have no `: ` after the sender — that's how to distinguish them

## Special Message Types

### Media (two formats)
1. **Old format**: `<Media omitted>` — media was not exported
2. **New format**: `FILENAME (file attached)` — media was exported with filename
   - Images: `IMG-20260422-WA0002.jpg (file attached)`
   - Stickers: `STK-20260422-WA0006.webp (file attached)`
   - Pattern: `STK-*` prefix = sticker, `IMG-*` = image

### Deleted Messages
1. `This message was deleted` — other person deleted their message
2. `You deleted this message` — chat exporter deleted their message

### Missed Calls
1. `Missed voice call`
2. `Missed video call`

## Regex for Parsing
```python
# Primary message pattern (handles both regular space and \u202F before AM/PM)
r'^(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}[\s\u202f][APap][Mm])\s-\s(.*?):\s(.*)$'

# System message pattern (no sender)
r'^(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}[\s\u202f][APap][Mm])\s-\s(.*)$'
```

## Language
- Primarily Hinglish (Hindi written in English script) with some English
- Stop words list should include both Hindi-transliterated and English stop words
  - Hindi common: hai, ka, ki, ke, ko, me, se, ne, ye, wo, to, na, hi, bhi, kya, kuch, toh, nhi, nahi, tha, thi, the, ho, hoga, hogi, aur, ya
  - English common: the, a, an, is, was, are, etc.

## Counts to Verify During Development
- Sanity check: ~47,051 lines, but actual messages will be fewer due to multi-line messages
- Both "This message was deleted" and "You deleted this message" exist
- Both `<Media omitted>` and `(file attached)` formats exist
- Missed voice/video calls present
