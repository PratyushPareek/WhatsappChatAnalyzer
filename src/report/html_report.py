import os
from pathlib import Path
from html import escape

from src.analyzers.base import AnalysisResult
from src.config.settings import Settings
from src.report.base import IReportGenerator

_CSS = """
/* ═══════════════════════════════════════════════════════════
   WAChatAnalysis — Design System Tokens
   Reference: DESIGN.md
   ═══════════════════════════════════════════════════════════ */

:root {
  /* Backgrounds */
  --color-bg:             #FAF7F2;
  --color-bg-warm:        #F5F0E8;
  --color-text:           #2C2A28;
  --color-text-secondary: #6B6560;
  --color-text-muted:     #9E9790;
  --color-border:         #E5DFD6;
  --color-border-light:   #EEEBE5;
  --color-surface:        #FFFFFF;
  --color-surface-warm:   #FDF9F3;

  /* Accent */
  --color-accent:         #D94F30;
  --color-accent-hover:   #C4432A;
  --color-accent-light:   #FDEEE9;
  --color-accent-muted:   #E8836C;

  /* Semantic */
  --color-success:        #2D8B55;
  --color-info:           #2A7B9B;

  /* Participant */
  --color-person-1:       #D94F30;
  --color-person-2:       #2A7B9B;
  --color-person-3:       #7B6DAA;
  --color-person-4:       #D4A843;
  --color-person-5:       #2D8B55;

  /* Typography */
  --font-display:  'Bricolage Grotesque', Georgia, serif;
  --font-body:     'DM Sans', -apple-system, sans-serif;
  --font-mono:     'JetBrains Mono', 'Fira Code', 'Consolas', monospace;

  --text-xs:   0.75rem;
  --text-sm:   0.875rem;
  --text-base: 1rem;
  --text-lg:   1.125rem;
  --text-xl:   1.25rem;
  --text-2xl:  1.5rem;
  --text-3xl:  1.875rem;
  --text-4xl:  2.25rem;
  --text-5xl:  3rem;

  --leading-tight:  1.15;
  --leading-snug:   1.3;
  --leading-normal: 1.6;
  --leading-loose:  1.8;

  /* Spacing */
  --space-1:  0.25rem;
  --space-2:  0.5rem;
  --space-3:  0.75rem;
  --space-4:  1rem;
  --space-6:  1.5rem;
  --space-8:  2rem;
  --space-10: 2.5rem;
  --space-12: 3rem;
  --space-16: 4rem;
  --space-20: 5rem;

  --content-width: 900px;
  --radius-sm:   8px;
  --radius-md:   12px;
  --radius-lg:   16px;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm:  0 1px 2px rgba(44, 42, 40, 0.05);
  --shadow-md:  0 4px 12px rgba(44, 42, 40, 0.08);
  --shadow-lg:  0 8px 24px rgba(44, 42, 40, 0.1);
}

/* ═══════════════════════════════════════════════════════════
   Reset & Base
   ═══════════════════════════════════════════════════════════ */

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: var(--font-body);
  background: var(--color-bg);
  background-image: radial-gradient(
    ellipse at 20% 50%,
    rgba(217, 79, 48, 0.03) 0%,
    transparent 50%
  );
  color: var(--color-text);
  line-height: var(--leading-normal);
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: var(--radius-full);
}

.container {
  max-width: var(--content-width);
  margin: 0 auto;
  padding: var(--space-6);
}

/* ═══════════════════════════════════════════════════════════
   Cover
   ═══════════════════════════════════════════════════════════ */

.cover {
  text-align: center;
  padding: var(--space-20) var(--space-6) var(--space-16);
  margin-bottom: var(--space-8);
}
.cover h1 {
  font-family: var(--font-display);
  font-size: var(--text-5xl);
  font-weight: 800;
  line-height: var(--leading-tight);
  color: var(--color-text);
  margin-bottom: var(--space-4);
}
.cover .participants {
  font-family: var(--font-display);
  font-size: var(--text-4xl);
  font-weight: 600;
  color: var(--color-accent);
  margin-bottom: var(--space-3);
}
.cover .date-range {
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--color-text-muted);
}

/* ═══════════════════════════════════════════════════════════
   Section Cards
   ═══════════════════════════════════════════════════════════ */

.section {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
  margin-bottom: var(--space-6);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border-light);
}
.section:nth-child(odd) {
  background: var(--color-surface-warm);
}

.section h2 {
  font-family: var(--font-display);
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--color-text);
  line-height: var(--leading-tight);
  margin-bottom: var(--space-6);
  padding-bottom: var(--space-3);
  border-bottom: 2px solid var(--color-accent);
}
.section h3 {
  font-family: var(--font-display);
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--color-accent-muted);
  margin: var(--space-6) 0 var(--space-3);
}

/* ═══════════════════════════════════════════════════════════
   Stat Cards
   ═══════════════════════════════════════════════════════════ */

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}
.stat-card {
  background: var(--color-surface);
  border-radius: var(--radius-md);
  padding: var(--space-6) var(--space-6);
  border: 1px solid var(--color-border-light);
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}
.stat-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}
.stat-card .label {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.stat-card .value {
  font-family: var(--font-mono);
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-text);
  margin-top: var(--space-1);
}
.stat-card .sub {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin-top: var(--space-1);
}

/* ═══════════════════════════════════════════════════════════
   Tables
   ═══════════════════════════════════════════════════════════ */

table {
  width: 100%;
  border-collapse: collapse;
  margin: var(--space-3) 0;
}
th, td {
  padding: var(--space-3) var(--space-4);
  text-align: left;
  border-bottom: 1px solid var(--color-border-light);
}
th {
  background: var(--color-bg-warm);
  color: var(--color-accent);
  font-family: var(--font-body);
  font-weight: 600;
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
td {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--color-text);
}
tr:hover td {
  background: var(--color-accent-light);
}

/* ═══════════════════════════════════════════════════════════
   KV Rows
   ═══════════════════════════════════════════════════════════ */

.kv-row {
  display: flex;
  padding: var(--space-2) 0;
  border-bottom: 1px solid var(--color-border-light);
}
.kv-row:last-child { border-bottom: none; }
.kv-key {
  width: 220px;
  flex-shrink: 0;
  font-family: var(--font-body);
  font-weight: 600;
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}
.kv-val {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: var(--color-text);
}

/* ═══════════════════════════════════════════════════════════
   Charts
   ═══════════════════════════════════════════════════════════ */

.chart-container {
  margin: var(--space-6) 0;
}

/* ═══════════════════════════════════════════════════════════
   Emoji Display
   ═══════════════════════════════════════════════════════════ */

.emoji-list {
  font-size: 1.3em;
  line-height: 2.2;
}
.emoji-item {
  display: inline-block;
  padding: var(--space-1) var(--space-2);
}
.emoji-count {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

/* ═══════════════════════════════════════════════════════════
   Word Cloud
   ═══════════════════════════════════════════════════════════ */

.wordcloud-box {
  padding: var(--space-4);
}
.wordcloud-title {
  font-family: var(--font-display);
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: var(--space-3);
}
.wordcloud-words {
  line-height: 2.2;
  text-align: center;
}

/* ═══════════════════════════════════════════════════════════
   Appendix
   ═══════════════════════════════════════════════════════════ */

.appendix-content {
  background: var(--color-bg-warm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: var(--space-4) var(--space-6);
  margin: var(--space-3) 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  line-height: var(--leading-loose);
  color: var(--color-text-secondary);
  max-height: 400px;
  overflow-y: auto;
}

.rant-chat {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  margin: var(--space-3) 0;
  max-height: 400px;
  overflow-y: auto;
}

.rant-bubble {
  background: var(--color-bg-warm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm) var(--radius-sm) var(--radius-sm) 4px;
  padding: var(--space-3) var(--space-4);
  max-width: 85%;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: var(--font-body);
  font-size: var(--text-sm);
  line-height: var(--leading-loose);
  color: var(--color-text-secondary);
}

.rant-bubble .rant-time {
  display: block;
  font-size: 0.7rem;
  color: var(--color-text-muted);
  margin-bottom: var(--space-1);
}

.appendix-caution {
  display: flex;
  align-items: flex-start;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-6);
  margin-bottom: var(--space-6);
  background: #fef3c7;
  border: 1px solid #f59e0b;
  border-left: 4px solid #f59e0b;
  border-radius: var(--radius-sm);
}

.appendix-caution-icon {
  font-size: 1.4rem;
  line-height: 1;
  flex-shrink: 0;
}

.appendix-caution-text {
  font-size: var(--text-sm);
  color: #92400e;
  line-height: var(--leading-normal);
}

/* ═══════════════════════════════════════════════════════════
   Tooltip
   ═══════════════════════════════════════════════════════════ */

.info-tip {
  display: inline-block;
  width: 16px;
  height: 16px;
  line-height: 16px;
  text-align: center;
  font-size: 11px;
  font-weight: 700;
  font-family: var(--font-mono);
  color: var(--color-text-muted);
  background: var(--color-border-light);
  border-radius: var(--radius-full);
  cursor: help;
  position: relative;
  vertical-align: middle;
  margin-left: var(--space-2);
}
.info-tip:hover::after {
  content: attr(data-tip);
  position: absolute;
  bottom: 120%;
  left: 50%;
  transform: translateX(-50%);
  background: var(--color-text);
  color: var(--color-surface);
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 400;
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-sm);
  white-space: normal;
  max-width: 300px;
  width: max-content;
  z-index: 10;
  pointer-events: none;
}

/* ═══════════════════════════════════════════════════════════
   Longest word wrap
   ═══════════════════════════════════════════════════════════ */

.word-wrap {
  word-break: break-all;
  overflow-wrap: break-word;
}
"""


class HTMLReportGenerator(IReportGenerator):
    def __init__(self, output_dir: str, config: Settings):
        self._output_dir = output_dir
        self._config = config
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    def generate(self, results: list[AnalysisResult], chart_paths: dict[str, list[str]],
                 metadata: dict) -> str:
        result_map = {r.section_id: r for r in results}
        parts: list[str] = []

        parts.append(self._cover(metadata))

        if "basic_stats" in result_map:
            parts.append(self._basic_stats(result_map["basic_stats"]))
        if "per_person" in result_map:
            parts.append(self._per_person(result_map["per_person"]))
        if "temporal" in result_map:
            parts.append(self._temporal(result_map["temporal"], chart_paths.get("temporal", [])))
        if "dynamics" in result_map:
            parts.append(self._dynamics(result_map["dynamics"]))
        if "happiness" in result_map:
            parts.append(self._happiness(result_map["happiness"]))
        if "emoji" in result_map:
            parts.append(self._emoji(result_map["emoji"], chart_paths.get("emoji", [])))
        if "media" in result_map:
            parts.append(self._media(result_map["media"]))
        if "words" in result_map:
            parts.append(self._words(result_map["words"], chart_paths.get("words", [])))
        if "fun_stats" in result_map:
            parts.append(self._fun_stats(result_map["fun_stats"]))

        parts.append(self._appendices(results) if self._config.include_appendix else "")

        body = "\n".join(parts)
        html = self._wrap_html(body, metadata)

        source = metadata.get("source_file", "report")
        stem = Path(source).stem
        output_path = os.path.join(self._output_dir, f"{stem}_report.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        return output_path

    # ─── HTML wrapper ────────────────────────────────────────────

    def _wrap_html(self, body: str, metadata: dict) -> str:
        participants = metadata.get("participants", [])
        title = f"Chat Analysis — {' & '.join(participants)}"
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,700;12..96,800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400;1,9..40,500&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<script src="https://cdn.plot.ly/plotly-2.35.0.min.js"></script>
<style>{_CSS}</style>
</head>
<body>
<div class="container">
{body}
</div>
</body>
</html>"""

    # ─── Helpers ─────────────────────────────────────────────────

    @staticmethod
    def _e(text) -> str:
        return escape(str(text))

    def _stat_card(self, label: str, value, sub: str = "") -> str:
        sub_html = f'<div class="sub">{self._e(sub)}</div>' if sub else ""
        return f'<div class="stat-card"><div class="label">{self._e(label)}</div><div class="value">{self._e(value)}</div>{sub_html}</div>'

    def _kv(self, key: str, value) -> str:
        return f'<div class="kv-row"><span class="kv-key">{self._e(key)}</span><span class="kv-val">{self._e(value)}</span></div>'

    def _charts_html(self, charts: list[str]) -> str:
        parts = []
        for chart_html in charts:
            if chart_html:
                parts.append(f'<div class="chart-container">{chart_html}</div>')
        return "\n".join(parts)

    # ─── Cover ───────────────────────────────────────────────────

    def _cover(self, metadata: dict) -> str:
        participants = metadata.get("participants", [])
        dr = metadata.get("date_range", (None, None))
        date_str = ""
        if dr[0] and dr[1]:
            date_str = f"{dr[0].strftime('%B %d, %Y')} — {dr[1].strftime('%B %d, %Y')}"
        return f"""<div class="cover">
<h1>WhatsApp Chat Analysis</h1>
<div class="participants">{self._e(' & '.join(participants))}</div>
<div class="date-range">{self._e(date_str)}</div>
</div>"""

    # ─── Section 1: Basic Stats ──────────────────────────────────

    def _basic_stats(self, result: AnalysisResult) -> str:
        s = result.stats
        fm = s.get("first_message")
        fm_text = f"{fm['sender']} on {fm['date']} at {fm['time']}" if fm else "N/A"

        participants = " & ".join(s.get("participants", []))
        years = s.get("total_years", 0)
        days_pct = s.get("active_days_pct", 0)
        weeks_pct = s.get("active_weeks_pct", 0)
        summary = f"{participants} have spoken for {days_pct}% of days and {weeks_pct}% of weeks in the last {years} years."

        return f"""<div class="section">
<h2>1. Overview & Basic Stats</h2>
<p style="font-family: var(--font-body); font-size: var(--text-lg); color: var(--color-text-secondary); margin-bottom: var(--space-6); line-height: var(--leading-normal);">{self._e(summary)}</p>
<div class="stats-grid">
{self._stat_card("Total Messages", f"{s['total_messages']:,}")}
{self._stat_card("Total Words", f"{s['total_words']:,}")}
{self._stat_card("Total Characters", f"{s['total_characters']:,}")}
{self._stat_card("Active Days", f"{s['active_days']:,} / {s['total_days']:,}", f"{s['active_days_pct']}% of total days")}
{self._stat_card("Active Weeks", f"{s['active_weeks']:,} / {s['total_weeks']:,}", f"{s['active_weeks_pct']}% of total weeks")}
{self._stat_card("Participants", s['num_participants'])}
</div>
{self._kv("Date Range", f"{s['date_range_start']} — {s['date_range_end']}")}
<div class="kv-row"><span class="kv-key">First Message By <span class="info-tip" data-tip="Full text in Appendix A">i</span></span><span class="kv-val">{self._e(fm_text)}</span></div>
</div>"""

    # ─── Section 2: Per-Person ───────────────────────────────────

    def _per_person(self, result: AnalysisResult) -> str:
        pp = result.stats.get("per_person", {})
        rows = ""
        for p, d in pp.items():
            rows += f"""<tr>
<td>{self._e(p)}</td>
<td>{d['message_count']:,}</td>
<td>{d['message_pct']}%</td>
<td>{d['word_count']:,}</td>
<td>{d['avg_words_per_msg']}</td>
<td>{d['char_count']:,}</td>
</tr>"""

        # Build a comparison table for longest messages
        participants = list(pp.keys())
        max_longest = max(len(pp[p].get("longest_messages", [])) for p in participants) if participants else 0
        longest_table = ""
        if max_longest > 0:
            # Header: #, then per-person columns (Date, Words, Chars for each)
            header_cols = "<th>#</th>"
            for p in participants:
                header_cols += f'<th colspan="3" style="text-align:center; border-left: 2px solid var(--color-border);">{self._e(p)}</th>'
            sub_header = "<td></td>"
            for _ in participants:
                sub_header += '<td style="border-left: 2px solid var(--color-border); font-weight:600; color:var(--color-text-muted); font-size:var(--text-xs); text-transform:uppercase;">Date</td><td style="font-weight:600; color:var(--color-text-muted); font-size:var(--text-xs); text-transform:uppercase;">Words</td><td style="font-weight:600; color:var(--color-text-muted); font-size:var(--text-xs); text-transform:uppercase;">Chars</td>'

            rows_html = ""
            for i in range(max_longest):
                row = f"<td>{i + 1}</td>"
                for p in participants:
                    msgs = pp[p].get("longest_messages", [])
                    if i < len(msgs):
                        lm = msgs[i]
                        row += f'<td style="border-left: 2px solid var(--color-border);">{self._e(lm["date"])}</td><td>{lm["word_count"]}</td><td>{lm["char_count"]}</td>'
                    else:
                        row += '<td style="border-left: 2px solid var(--color-border);">—</td><td>—</td><td>—</td>'
                rows_html += f"<tr>{row}</tr>"

            longest_table = f'<table><tr>{header_cols}</tr><tr>{sub_header}</tr>{rows_html}</table>'

        tip = '<span class="info-tip" data-tip="Full text in Appendix B">i</span>'

        return f"""<div class="section">
<h2>2. Per-Person Breakdown</h2>
<table>
<tr><th>Person</th><th>Messages</th><th>Share</th><th>Words</th><th>Avg W/M</th><th>Characters</th></tr>
{rows}
</table>
<h3>Longest Messages {tip}</h3>
{longest_table}
</div>"""

    # ─── Section 3: Temporal ─────────────────────────────────────

    def _temporal(self, result: AnalysisResult, charts: list[str]) -> str:
        s = result.stats

        # Top 5 active days
        active_day_rows = ""
        for d in s.get("top_active_days", []):
            active_day_rows += f"<tr><td>{self._e(d['date'])}</td><td>{d['count']}</td></tr>"

        # Top 5 active hours
        active_hour_rows = ""
        for d in s.get("top_active_hours", []):
            active_hour_rows += f"<tr><td>{self._e(d['date'])}</td><td>{self._e(d['hour'])}</td><td>{d['count']}</td></tr>"

        streak = s.get("longest_streak", {})
        streak_range = f"{streak.get('start', 'N/A')} — {streak.get('end', 'N/A')}"
        silence = s.get("longest_silence", {})
        silence_range = ""
        if silence.get("from"):
            silence_range = f"{silence['from']} — {silence['to']}"

        # Response time comparison table
        rt = s.get("response_time", {})
        participants = list(rt.keys())
        response_html = ""
        if participants:
            header = '<th>Metric</th>'
            for p in participants:
                header += f'<th style="text-align:center;">{self._e(p)}</th>'

            metrics = [
                ("25th Percentile", "p25_display"),
                ("Median", "median_display"),
                ("75th Percentile", "p75_display"),
                ("Replies \u2264 1 min", "under_1m"),
            ]
            rows_html = ""
            for label, key in metrics:
                row = f'<td style="font-weight:600; color:var(--color-text-muted);">{label}</td>'
                for p in participants:
                    val = rt[p].get(key, "N/A")
                    if isinstance(val, int):
                        val = f"{val:,}"
                    row += f'<td style="text-align:center;">{self._e(val)}</td>'
                rows_html += f"<tr>{row}</tr>"

            response_html = f'<table><tr>{header}</tr>{rows_html}</table>'

        return f"""<div class="section">
<h2>3. Temporal Analysis</h2>
<div class="stats-grid">
{self._stat_card("Longest Streak", f"{streak.get('days', 0)} days", streak_range)}
{self._stat_card("Longest Silence", silence.get('total_display', 'N/A'), silence_range)}
</div>
<h3>Top 5 Most Active Days</h3>
<table><tr><th>Date</th><th>Messages</th></tr>{active_day_rows}</table>
<h3>Top 5 Most Active Hours</h3>
<table><tr><th>Date</th><th>Hour</th><th>Messages</th></tr>{active_hour_rows}</table>
{self._charts_html(charts)}
<p style="font-size:var(--text-xs); color:var(--color-text-muted); margin-top:calc(-1 * var(--space-3)); margin-bottom:var(--space-4);"><span class="info-tip" data-tip="Distribution of how many messages are sent per day (excluding days with 0 messages). The curve is a kernel density estimate (KDE).">i</span> Daily message count distribution (zero-message days excluded)</p>
<h3>Response Time <span class="info-tip" data-tip="Only replies within {self._config.conversation_gap_hours}h are counted">i</span></h3>
{response_html}
</div>"""

    # ─── Section 4: Emoji ────────────────────────────────────────

    def _emoji(self, result: AnalysisResult, charts: list[str]) -> str:
        s = result.stats

        total_cards = ""
        for p, count in s.get("total_per_person", {}).items():
            total_cards += self._stat_card(f"{p}'s Emojis", f"{count:,}")

        unique_cards = ""
        for p, count in s.get("unique_per_person", {}).items():
            unique_cards += self._stat_card(f"{p}'s Unique Emojis", f"{count:,}")

        top_overall_html = ""
        for e, c in s.get("top_overall", []):
            top_overall_html += f'<span class="emoji-item">{e} <span class="emoji-count">({c})</span></span>'

        per_person_html = ""
        for p, tops in s.get("top_per_person", {}).items():
            items = ""
            for e, c in tops:
                items += f'<span class="emoji-item">{e} <span class="emoji-count">({c})</span></span>'
            per_person_html += f'<h3>Top Emojis — {self._e(p)}</h3><div class="emoji-list">{items}</div>'

        return f"""<div class="section">
<h2>6. Emoji Analysis</h2>
<div class="stats-grid">
{total_cards}
</div>
<div class="stats-grid">
{unique_cards}
</div>
<h3>Top Emojis (Overall)</h3>
<div class="emoji-list">{top_overall_html}</div>
{per_person_html}
{self._charts_html(charts)}
</div>"""

    # ─── Section 5: Media ────────────────────────────────────────

    def _media(self, result: AnalysisResult) -> str:
        pp = result.stats.get("per_person", {})
        rows = ""
        for p, d in pp.items():
            rows += f"""<tr>
<td>{self._e(p)}</td>
<td>{d['stickers']}</td>
<td>{d['images']}</td>
<td>{d['videos']}</td>
<td>{d['audio']}</td>
<td>{d['contacts']}</td>
<td>{d['pdfs']}</td>
<td>{d['unknown_media']}</td>
<td>{d['total_media']}</td>
</tr>"""

        unique_stickers_kv = ""
        for p, count in result.stats.get("unique_stickers_per_person", {}).items():
            unique_stickers_kv += self._stat_card(f"{p}'s Unique Stickers", count)

        stickers_html = ""
        for p, tops in result.stats.get("top_stickers_per_person", {}).items():
            if tops:
                stickers_html += f'<h3>Top Stickers — {self._e(p)}</h3>'
                sticker_rows = ""
                for i, (sid, count) in enumerate(tops, 1):
                    sticker_rows += f"<tr><td>{i}</td><td>{self._e(sid)}</td><td>{count}</td></tr>"
                stickers_html += f'<table><tr><th>#</th><th>Sticker ID</th><th>Times Sent</th></tr>{sticker_rows}</table>'

        return f"""<div class="section">
<h2>7. Sticker & Media Analysis</h2>
<table>
<tr><th>Person</th><th>Stickers</th><th>Images</th><th>Videos</th><th>Audio</th><th>Contacts</th><th>PDFs</th><th>Other</th><th>Total</th></tr>
{rows}
</table>
<div class="stats-grid">
{unique_stickers_kv}
</div>
{stickers_html}
</div>"""

    # ─── Section 6: Words ────────────────────────────────────────

    def _words(self, result: AnalysisResult, charts: list[str]) -> str:
        s = result.stats

        avg_kv = ""
        for p, avg in s.get("avg_words_per_message", {}).items():
            avg_kv += self._stat_card(f"{p}'s Avg W/M", avg)
        vocab_kv = ""
        for p, size in s.get("vocab_size", {}).items():
            vocab_kv += self._stat_card(f"{p}'s Vocabulary", f"{size:,}", "unique words used")

        # Top words per person
        per_person_sections = ""
        for p, tops in s.get("top_words_per_person", {}).items():
            rows = ""
            for i, (word, count) in enumerate(tops[:10], 1):
                rows += f"<tr><td>{i}</td><td>{self._e(word)}</td><td>{count}</td></tr>"
            per_person_sections += f"""<h3>Top Words — {self._e(p)}</h3>
<table><tr><th>#</th><th>Word</th><th>Count</th></tr>{rows}</table>"""

        return f"""<div class="section">
<h2>8. Word & Language Analysis</h2>
<div class="stats-grid">
{avg_kv}
</div>
<div class="stats-grid">
{vocab_kv}
</div>
{per_person_sections}
{self._charts_html(charts)}
</div>"""

    # ─── Section 7: Dynamics ─────────────────────────────────────

    def _dynamics(self, result: AnalysisResult) -> str:
        s = result.stats

        init_kv = ""
        for p, d in s.get("initiator", {}).items():
            init_kv += self._kv(p, f"{d['count']} ({d['pct']}%)")

        morning_kv = ""
        for p, d in s.get("morning_texter", {}).items():
            morning_kv += self._kv(p, f"{d['count']} ({d['pct']}%)")

        ghost_kv = ""
        for p, d in s.get("ghost", {}).items():
            ghost_kv += self._kv(p, f"{d['count']} ({d['pct']}%)")

        consec_kv = ""
        for p, d in s.get("consecutive_messages", {}).items():
            consec_kv += self._kv(p, f"Double: {d['double']}, Triple+: {d['triple_plus']}")

        q_kv = ""
        for p, count in s.get("questions", {}).items():
            q_kv += self._kv(p, str(count))

        l_kv = ""
        for p, count in s.get("laughs", {}).items():
            l_kv += self._kv(p, str(count))

        # Conversation length comparison table
        cl = s.get("conversation_length", {})
        cl_msgs = cl.get("messages", {})
        cl_dur = cl.get("duration", {})
        convo_table = ""
        if cl_msgs:
            convo_table = f"""<table>
<tr><th>Metric</th><th>25th Percentile</th><th>Median</th><th>75th Percentile</th></tr>
<tr><td style="font-weight:600; color:var(--color-text-muted);">Messages</td><td>{cl_msgs.get('p25', 'N/A')}</td><td>{cl_msgs.get('median', 'N/A')}</td><td>{cl_msgs.get('p75', 'N/A')}</td></tr>
<tr><td style="font-weight:600; color:var(--color-text-muted);">Duration</td><td>{self._e(cl_dur.get('p25', 'N/A'))}</td><td>{self._e(cl_dur.get('median', 'N/A'))}</td><td>{self._e(cl_dur.get('p75', 'N/A'))}</td></tr>
</table>"""

        return f"""<div class="section">
<h2>4. Conversation Dynamics</h2>
<div class="stats-grid">
{self._stat_card("Total Conversations", f"{s.get('total_conversations', 0):,}")}
</div>
<h3>Conversation Initiator <span class="info-tip" data-tip="A new conversation starts after a {self._config.conversation_gap_hours}h gap">i</span></h3>
{init_kv}
<h3>Morning Texter <span class="info-tip" data-tip="First message of the day after 5 AM">i</span></h3>
{morning_kv}
<h3>Last to Speak <span class="info-tip" data-tip="Who sent the last message before a {self._config.conversation_gap_hours}h+ silence">i</span></h3>
{ghost_kv}
<h3>Conversation Length <span class="info-tip" data-tip="Per conversation ({self._config.conversation_gap_hours}h gap = new conversation)">i</span></h3>
{convo_table}
<h3>Consecutive Messages (Double / Triple+)</h3>
{consec_kv}
<h3>Questions Asked</h3>
{q_kv}
<h3>Laugh Messages</h3>
{l_kv}
</div>"""

    # ─── Section 8: Happiness Analysis ───────────────────────────

    def _happiness(self, result: AnalysisResult) -> str:
        s = result.stats

        happiest_month = s.get("happiest_month")
        hm_card = ""
        if happiest_month:
            hm_card = self._stat_card("Happiest Month", happiest_month["month"], f"{happiest_month['count']} happy messages")

        tip = '<span class="info-tip" data-tip="Counted by happy/laughing keywords + emojis. Only days in the 25th–75th percentile of daily message volume are included.">i</span>'

        return f"""<div class="section">
<h2>5. Happiness Analysis {tip}</h2>
<div class="stats-grid">
{self._stat_card("Total Happy Messages", f"{s.get('total_happy', 0):,}", f"{s.get('total_happy_pct', 0)}% of text messages")}
{hm_card}
</div>
{self._happiest_moments(s.get("happiest_moments", []))}
</div>"""

    def _happiest_moments(self, moments: list) -> str:
        if not moments:
            return ""
        rows = ""
        for i, m in enumerate(moments, 1):
            rows += f"""<tr>
<td>{i}</td>
<td>{self._e(m['date'])}</td>
<td>{m['messages']}</td>
<td>{m['score']}</td>
<td>{m['happiness_index']}</td>
</tr>"""

        tip = f'<span class="info-tip" data-tip="Ranked by happy_count / total^0.1 — rewards more happy messages but softly penalizes longer days. Only days above the 75th percentile in message count are included. First 2 messages of each day in Appendix D.">i</span>'
        return f"""<h3>Happiest Days {tip}</h3>
<table>
<tr><th>#</th><th>Date</th><th>Messages</th><th>Happy Count</th><th>Index</th></tr>
{rows}
</table>"""

    # ─── Section 9: Miscellaneous ────────────────────────────────

    def _fun_stats(self, result: AnalysisResult) -> str:
        s = result.stats

        del_kv = ""
        for p, count in s.get("deleted_messages", {}).items():
            del_kv += self._kv(p, str(count))

        word_kv = ""
        for p, d in s.get("most_used_word", {}).items():
            word_kv += self._kv(p, f'"{d["word"]}" ({d["count"]} times)')

        lw_html = ""
        for p, word in s.get("longest_word_per_person", {}).items():
            lw_html += (
                f'<div class="kv-row"><span class="kv-key">{self._e(p)}</span>'
                f'<span class="kv-val word-wrap">&quot;{self._e(word)}&quot; ({len(word)} chars)</span></div>'
            )

        shout_kv = ""
        for p, d in s.get("shouting_index", {}).items():
            shout_kv += self._kv(p, f"{d['count']} messages ({d['pct']}%)")

        manners_kv = ""
        for p, d in s.get("manners", {}).items():
            manners_kv += self._kv(p, f"{d['count']} messages ({d['pct']}%)")

        rants_kv = ""
        for p, d in s.get("rants", {}).items():
            if d["count"] > 0:
                date_ref = f" on {d['longest_streak_date']}" if d.get("longest_streak_date") else ""
                rants_kv += self._kv(p, f"{d['count']} rants (longest: {d['longest_streak']} messages{date_ref})")
            else:
                rants_kv += self._kv(p, "0 rants")

        return f"""<div class="section">
<h2>9. Miscellaneous</h2>
<h3>Deleted Messages</h3>
{del_kv}
<h3>Longest Word</h3>
{lw_html}
<h3>Manners (thank you, sorry, please, …)</h3>
{manners_kv}
<h3>Rants <span class="info-tip" data-tip="4+ consecutive messages (≥2 words each) within 2 min of each other. Short fillers (≤3 chars) are ignored.">i</span></h3>
{rants_kv}
</div>"""

    # ─── Appendices ──────────────────────────────────────────────

    def _appendices(self, results: list[AnalysisResult]) -> str:
        first_messages = {}
        longest_messages = {}
        longest_rants = {}
        happiest_previews = []
        for r in results:
            if r.appendix:
                if "first_messages" in r.appendix:
                    first_messages = r.appendix["first_messages"]
                if "longest_messages" in r.appendix:
                    longest_messages = r.appendix["longest_messages"]
                if "longest_rants" in r.appendix:
                    longest_rants = r.appendix["longest_rants"]
                if "happiest_previews" in r.appendix:
                    happiest_previews = r.appendix["happiest_previews"]

        parts = []

        has_appendix = first_messages or longest_messages or longest_rants or happiest_previews
        if has_appendix:
            parts.append('<div class="appendix-caution"><div class="appendix-caution-icon">⚠️</div><div class="appendix-caution-text"><strong>Caution:</strong> Actual messages from your chat appear below.</div></div>')

        if first_messages:
            items = ""
            for p, d in first_messages.items():
                items += f"""<h3>{self._e(p)}</h3>
{self._kv("Date", f"{d['date']} at {d['time']}")}
<div class="appendix-content">{self._e(d['content'][:2000])}</div>"""
            parts.append(f'<div class="section"><h2>Appendix A: First Messages</h2>{items}</div>')

        if longest_messages:
            items = ""
            for p, msg_list in longest_messages.items():
                for i, d in enumerate(msg_list, 1):
                    items += f"""<h3>{self._e(p)} — #{i}</h3>
{self._kv("Date", f"{d['date']} at {d['time']}")}
<div class="appendix-content">{self._e(d['content'][:3000])}</div>"""
            parts.append(f'<div class="section"><h2>Appendix B: Longest Messages</h2>{items}</div>')

        if longest_rants:
            items = ""
            for p, msg_list in longest_rants.items():
                bubbles = ""
                for d in msg_list:
                    bubbles += f"""<div class="rant-bubble">
<span class="rant-time">{d['date']} at {d['time']}</span>
{self._e(d['content'][:3000])}
</div>"""
                items += f"""<h3>{self._e(p)}</h3>
<div class="rant-chat">{bubbles}</div>"""
            parts.append(f'<div class="section"><h2>Appendix C: Longest Rant (First 2 Messages)</h2>{items}</div>')

        if happiest_previews:
            items = ""
            for idx, convo_msgs in enumerate(happiest_previews, 1):
                bubbles = ""
                for d in convo_msgs:
                    bubbles += f"""<div class="rant-bubble">
<span class="rant-time">{self._e(d['sender'])} — {d['date']} at {d['time']}</span>
{self._e(d['content'][:3000])}
</div>"""
                items += f"""<h3>#{idx}</h3>
<div class="rant-chat">{bubbles}</div>"""
            parts.append(f'<div class="section"><h2>Appendix D: Happiest Days (First 2 Messages)</h2>{items}</div>')

        return "\n".join(parts)
