import os
import sys
from pathlib import Path

from src.config.settings import Settings
from src.parser.whatsapp_parser import WhatsAppParser
from src.analyzers.basic_stats import BasicStatsAnalyzer
from src.analyzers.per_person import PerPersonAnalyzer
from src.analyzers.temporal import TemporalAnalyzer
from src.analyzers.emoji_analyzer import EmojiAnalyzer
from src.analyzers.media import MediaAnalyzer
from src.analyzers.word_analysis import WordAnalyzer
from src.analyzers.dynamics import DynamicsAnalyzer
from src.analyzers.happiness import HappinessAnalyzer
from src.analyzers.fun_stats import FunStatsAnalyzer
from src.visualizers.plotly_visualizer import PlotlyVisualizer
from src.report.html_report import HTMLReportGenerator
from src.pipeline import AnalysisPipeline


def get_chat_files(chats_dir: str, args: list[str]) -> list[str]:
    if args:
        # Specific file(s) passed as arguments
        paths = []
        for arg in args:
            p = Path(arg)
            if not p.exists():
                # Try relative to chats_dir
                p = Path(chats_dir) / arg
            if p.exists():
                paths.append(str(p))
            else:
                print(f"Warning: File not found: {arg}")
        return paths

    # No args — process all .txt files in chats_dir
    chats_path = Path(chats_dir)
    if not chats_path.exists():
        print(f"Error: Chats directory not found: {chats_dir}")
        return []
    files = sorted(chats_path.glob("*.txt"))
    if not files:
        print(f"No .txt files found in {chats_dir}/")
    return [str(f) for f in files]


def main():
    config = Settings.from_yaml("config.yaml")

    # Create chart output dir
    chart_dir = os.path.join(config.output_dir, "charts")

    # Compose the object graph
    parser = WhatsAppParser(config)
    analyzers = [
        BasicStatsAnalyzer(config),
        PerPersonAnalyzer(config),
        TemporalAnalyzer(config),
        EmojiAnalyzer(config),
        MediaAnalyzer(config),
        WordAnalyzer(config),
        DynamicsAnalyzer(config),
        HappinessAnalyzer(config),
        FunStatsAnalyzer(config),
    ]
    visualizer = PlotlyVisualizer(style=config.chart_style)
    report_gen = HTMLReportGenerator(output_dir=config.output_dir, config=config)

    pipeline = AnalysisPipeline(parser, analyzers, visualizer, report_gen)

    # Get files to process
    files = get_chat_files(config.chats_dir, sys.argv[1:])
    if not files:
        print("No files to process.")
        return

    for file_path in files:
        print(f"\nProcessing: {file_path}")
        report_path = pipeline.run(file_path)
        print(f"Report generated: {report_path}")


if __name__ == "__main__":
    main()
