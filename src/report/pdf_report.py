import os
from pathlib import Path

from fpdf import FPDF

from src.analyzers.base import AnalysisResult
from src.config.settings import Settings
from src.report.base import IReportGenerator


class PDFReportGenerator(IReportGenerator):
    def __init__(self, output_dir: str, config: Settings):
        self._output_dir = output_dir
        self._config = config
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    def generate(self, results: list[AnalysisResult], chart_paths: dict[str, list[str]],
                 metadata: dict) -> str:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=20)

        self._cover_page(pdf, metadata)

        # Build a lookup for results by section_id
        result_map = {r.section_id: r for r in results}

        # Section 1: Basic Stats
        if "basic_stats" in result_map:
            self._basic_stats_page(pdf, result_map["basic_stats"])

        # Section 2: Per-Person Breakdown
        if "per_person" in result_map:
            self._per_person_page(pdf, result_map["per_person"])

        # Section 3: Temporal Analysis
        if "temporal" in result_map:
            self._temporal_page(pdf, result_map["temporal"], chart_paths.get("temporal", []))

        # Section 4: Emoji Analysis
        if "emoji" in result_map:
            self._emoji_page(pdf, result_map["emoji"], chart_paths.get("emoji", []))

        # Section 5: Media Analysis
        if "media" in result_map:
            self._media_page(pdf, result_map["media"])

        # Section 6: Word Analysis
        if "words" in result_map:
            self._words_page(pdf, result_map["words"], chart_paths.get("words", []))

        # Section 7: Conversation Dynamics
        if "dynamics" in result_map:
            self._dynamics_page(pdf, result_map["dynamics"])

        # Section 8: Fun Stats
        if "fun_stats" in result_map:
            self._fun_stats_page(pdf, result_map["fun_stats"])

        # Appendices
        self._appendices(pdf, results)

        # Save
        source = metadata.get("source_file", "report")
        stem = Path(source).stem
        output_path = os.path.join(self._output_dir, f"{stem}_report.pdf")
        pdf.output(output_path)
        return output_path

    # ─── Cover Page ──────────────────────────────────────────────

    def _cover_page(self, pdf: FPDF, metadata: dict):
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 28)
        pdf.ln(60)
        pdf.cell(0, 15, "WhatsApp Chat Analysis", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)
        pdf.set_font("Helvetica", "", 16)
        participants = metadata.get("participants", [])
        pdf.cell(0, 10, " & ".join(participants), align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)
        dr = metadata.get("date_range", (None, None))
        if dr[0] and dr[1]:
            pdf.set_font("Helvetica", "", 12)
            pdf.cell(0, 10, f"{dr[0].strftime('%B %d, %Y')} — {dr[1].strftime('%B %d, %Y')}",
                     align="C", new_x="LMARGIN", new_y="NEXT")

    # ─── Section Helpers ─────────────────────────────────────────

    def _section_header(self, pdf: FPDF, title: str):
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 20)
        pdf.cell(0, 12, title, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

    def _kv_row(self, pdf: FPDF, key: str, value: str):
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(80, 8, key, new_x="RIGHT")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, str(value), new_x="LMARGIN", new_y="NEXT")

    def _sub_header(self, pdf: FPDF, text: str):
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, text, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    def _add_charts(self, pdf: FPDF, chart_paths: list[str]):
        for path in chart_paths:
            if path and os.path.exists(path):
                # Check if we need a new page
                if pdf.get_y() > 150:
                    pdf.add_page()
                pdf.image(path, x=10, w=190)
                pdf.ln(5)

    def _table_header(self, pdf: FPDF, columns: list[str], widths: list[int]):
        pdf.set_font("Helvetica", "B", 10)
        for col, w in zip(columns, widths):
            pdf.cell(w, 8, col, border=1, align="C")
        pdf.ln()

    def _table_row(self, pdf: FPDF, values: list[str], widths: list[int]):
        pdf.set_font("Helvetica", "", 10)
        for val, w in zip(values, widths):
            pdf.cell(w, 8, str(val), border=1, align="C")
        pdf.ln()

    # ─── Section 1: Basic Stats ──────────────────────────────────

    def _basic_stats_page(self, pdf: FPDF, result: AnalysisResult):
        self._section_header(pdf, "1. Overview & Basic Stats")
        s = result.stats
        self._kv_row(pdf, "Total Messages", f"{s['total_messages']:,}")
        self._kv_row(pdf, "Total Words", f"{s['total_words']:,}")
        self._kv_row(pdf, "Total Characters", f"{s['total_characters']:,}")
        self._kv_row(pdf, "Date Range", f"{s['date_range_start']} — {s['date_range_end']}")
        self._kv_row(pdf, "Participants", ", ".join(s['participants']))
        self._kv_row(pdf, "Active Days", f"{s['active_days']:,}")

        if s.get("first_message"):
            fm = s["first_message"]
            self._kv_row(pdf, "First Message By", f"{fm['sender']} on {fm['date']} at {fm['time']}")

    # ─── Section 2: Per-Person ───────────────────────────────────

    def _per_person_page(self, pdf: FPDF, result: AnalysisResult):
        self._section_header(pdf, "2. Per-Person Breakdown")
        pp = result.stats.get("per_person", {})
        participants = list(pp.keys())

        if not participants:
            return

        widths = [40, 30, 25, 30, 25, 40]
        self._table_header(pdf, ["Person", "Messages", "%", "Words", "Avg W/M", "Characters"], widths)

        for p in participants:
            d = pp[p]
            self._table_row(pdf, [
                p,
                f"{d['message_count']:,}",
                f"{d['message_pct']}%",
                f"{d['word_count']:,}",
                str(d['avg_words_per_msg']),
                f"{d['char_count']:,}",
            ], widths)

        pdf.ln(5)
        self._sub_header(pdf, "Longest Messages")
        for p in participants:
            lm = pp[p].get("longest_message")
            if lm:
                self._kv_row(pdf, p, f"{lm['date']} — {lm['word_count']} words, {lm['char_count']} chars")

    # ─── Section 3: Temporal ─────────────────────────────────────

    def _temporal_page(self, pdf: FPDF, result: AnalysisResult, charts: list[str]):
        self._section_header(pdf, "3. Temporal Analysis")
        s = result.stats

        # Most active day/hour per person
        self._sub_header(pdf, "Most Active Day")
        for p, d in s.get("most_active_day", {}).items():
            self._kv_row(pdf, p, f"{d['date']} ({d['count']} messages)")

        self._sub_header(pdf, "Most Active Hour")
        for p, d in s.get("most_active_hour", {}).items():
            self._kv_row(pdf, p, f"{d['hour']} ({d['count']} messages)")

        # Streak & silence
        streak = s.get("longest_streak", {})
        self._kv_row(pdf, "Longest Streak", f"{streak.get('days', 0)} days (from {streak.get('start', 'N/A')})")

        silence = s.get("longest_silence", {})
        self._kv_row(pdf, "Longest Silence", silence.get("total_display", "N/A"))
        if silence.get("from"):
            self._kv_row(pdf, "  From", silence["from"])
            self._kv_row(pdf, "  To", silence["to"])

        # Response times
        self._sub_header(pdf, "Response Time")
        for p, d in s.get("response_time", {}).items():
            self._kv_row(pdf, f"{p} (median)", d.get("median_display", "N/A"))
            self._kv_row(pdf, f"{p} (average)", d.get("average_display", "N/A"))

        # Charts
        self._add_charts(pdf, charts)

    # ─── Section 4: Emoji ────────────────────────────────────────

    def _emoji_page(self, pdf: FPDF, result: AnalysisResult, charts: list[str]):
        self._section_header(pdf, "4. Emoji Analysis")
        s = result.stats

        # Total per person
        self._sub_header(pdf, "Total Emojis")
        for p, count in s.get("total_per_person", {}).items():
            self._kv_row(pdf, p, f"{count:,}")

        # Top overall
        self._sub_header(pdf, "Top Emojis (Overall)")
        top_overall = s.get("top_overall", [])
        if top_overall:
            pdf.set_font("Helvetica", "", 11)
            line = "  ".join(f"{e} ({c})" for e, c in top_overall)
            pdf.multi_cell(0, 8, line, new_x="LMARGIN", new_y="NEXT")

        # Top per person
        for p, tops in s.get("top_per_person", {}).items():
            self._sub_header(pdf, f"Top Emojis — {p}")
            if tops:
                pdf.set_font("Helvetica", "", 11)
                line = "  ".join(f"{e} ({c})" for e, c in tops)
                pdf.multi_cell(0, 8, line, new_x="LMARGIN", new_y="NEXT")

        self._add_charts(pdf, charts)

    # ─── Section 5: Media ────────────────────────────────────────

    def _media_page(self, pdf: FPDF, result: AnalysisResult):
        self._section_header(pdf, "5. Sticker & Media Analysis")
        pp = result.stats.get("per_person", {})
        participants = list(pp.keys())

        if not participants:
            return

        widths = [35, 22, 22, 22, 22, 22, 22, 25]
        self._table_header(pdf,
                           ["Person", "Stickers", "Images", "Videos", "Audio", "Other", "Total", "M/T Ratio"],
                           widths)
        for p in participants:
            d = pp[p]
            self._table_row(pdf, [
                p,
                str(d["stickers"]),
                str(d["images"]),
                str(d["videos"]),
                str(d["audio"]),
                str(d["unknown_media"]),
                str(d["total_media"]),
                str(d["media_to_text_ratio"]),
            ], widths)

    # ─── Section 6: Words ────────────────────────────────────────

    def _words_page(self, pdf: FPDF, result: AnalysisResult, charts: list[str]):
        self._section_header(pdf, "6. Word & Language Analysis")
        s = result.stats

        # Avg words per message
        self._sub_header(pdf, "Avg Words per Message")
        for p, avg in s.get("avg_words_per_message", {}).items():
            self._kv_row(pdf, p, str(avg))

        # Vocabulary size
        self._sub_header(pdf, "Unique Vocabulary Size")
        for p, size in s.get("vocab_size", {}).items():
            self._kv_row(pdf, p, f"{size:,}")

        # Top words per person
        for p, tops in s.get("top_words_per_person", {}).items():
            if pdf.get_y() > 200:
                pdf.add_page()
            self._sub_header(pdf, f"Top Words — {p}")
            if tops:
                widths = [60, 30]
                self._table_header(pdf, ["Word", "Count"], widths)
                for word, count in tops[:15]:
                    self._table_row(pdf, [word, str(count)], widths)

        self._add_charts(pdf, charts)

    # ─── Section 7: Dynamics ─────────────────────────────────────

    def _dynamics_page(self, pdf: FPDF, result: AnalysisResult):
        self._section_header(pdf, "7. Conversation Dynamics")
        s = result.stats

        self._kv_row(pdf, "Total Conversations", f"{s.get('total_conversations', 0):,}")

        self._sub_header(pdf, "Conversation Initiator")
        for p, d in s.get("initiator", {}).items():
            self._kv_row(pdf, p, f"{d['count']} ({d['pct']}%)")

        self._sub_header(pdf, "Consecutive Messages (Double/Triple+)")
        for p, d in s.get("consecutive_messages", {}).items():
            self._kv_row(pdf, p, f"Double: {d['double']}, Triple+: {d['triple_plus']}")

        self._sub_header(pdf, "Questions Asked")
        for p, count in s.get("questions", {}).items():
            self._kv_row(pdf, p, str(count))

        self._sub_header(pdf, "Laugh Messages")
        for p, count in s.get("laughs", {}).items():
            self._kv_row(pdf, p, str(count))

    # ─── Section 8: Fun Stats ────────────────────────────────────

    def _fun_stats_page(self, pdf: FPDF, result: AnalysisResult):
        self._section_header(pdf, "8. Fun & Novelty Stats")
        s = result.stats

        self._sub_header(pdf, "Deleted Messages")
        for p, count in s.get("deleted_messages", {}).items():
            self._kv_row(pdf, p, str(count))

        self._sub_header(pdf, "Most Used Word")
        for p, d in s.get("most_used_word", {}).items():
            self._kv_row(pdf, p, f'"{d["word"]}" ({d["count"]} times)')

        lw = s.get("longest_word", {})
        if lw.get("word"):
            self._sub_header(pdf, "Longest Word")
            self._kv_row(pdf, "Word", f'"{lw["word"]}" ({len(lw["word"])} chars)')
            self._kv_row(pdf, "By", lw.get("sender", ""))

        self._sub_header(pdf, "SHOUTING Index")
        for p, d in s.get("shouting_index", {}).items():
            self._kv_row(pdf, p, f"{d['count']} messages ({d['pct']}%)")

        self._sub_header(pdf, "Manners (thank you, sorry, please, …)")
        for p, d in s.get("manners", {}).items():
            self._kv_row(pdf, p, f"{d['count']} messages ({d['pct']}%)")

        self._sub_header(pdf, "Rants (4+ consecutive messages)")
        for p, d in s.get("rants", {}).items():
            if d["count"] > 0:
                self._kv_row(pdf, p, f"{d['count']} rants (longest: {d['longest_streak']} messages)")
            else:
                self._kv_row(pdf, p, "0 rants")

    # ─── Appendices ──────────────────────────────────────────────

    def _appendices(self, pdf: FPDF, results: list[AnalysisResult]):
        # Collect all appendix data
        first_messages = {}
        longest_messages = {}
        for r in results:
            if r.appendix:
                if "first_messages" in r.appendix:
                    first_messages = r.appendix["first_messages"]
                if "longest_messages" in r.appendix:
                    longest_messages = r.appendix["longest_messages"]

        if first_messages:
            self._section_header(pdf, "Appendix A: First Messages")
            for p, d in first_messages.items():
                self._sub_header(pdf, p)
                self._kv_row(pdf, "Date", f"{d['date']} at {d['time']}")
                pdf.set_font("Helvetica", "", 10)
                pdf.multi_cell(0, 6, d["content"][:2000], new_x="LMARGIN", new_y="NEXT")
                pdf.ln(3)

        if longest_messages:
            self._section_header(pdf, "Appendix B: Longest Messages")
            for p, d in longest_messages.items():
                self._sub_header(pdf, p)
                self._kv_row(pdf, "Date", f"{d['date']} at {d['time']}")
                pdf.set_font("Helvetica", "", 10)
                pdf.multi_cell(0, 6, d["content"][:3000], new_x="LMARGIN", new_y="NEXT")
                pdf.ln(3)
