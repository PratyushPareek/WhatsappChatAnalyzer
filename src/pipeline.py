from __future__ import annotations

from src.analyzers.base import AnalysisResult, IAnalyzer
from src.models.chat import Chat
from src.parser.base import IChatParser
from src.report.base import IReportGenerator
from src.visualizers.base import IVisualizer


class AnalysisPipeline:
    def __init__(
        self,
        parser: IChatParser,
        analyzers: list[IAnalyzer],
        visualizer: IVisualizer,
        report_generator: IReportGenerator,
    ):
        self._parser = parser
        self._analyzers = analyzers
        self._visualizer = visualizer
        self._report_generator = report_generator

    def run(self, file_path: str) -> str:
        # 1. Parse
        print(f"  Parsing {file_path}...")
        chat = self._parser.parse(file_path)
        print(f"  Found {len(chat.messages)} messages from {len(chat.participants)} participants")

        # 2. Analyze
        results: list[AnalysisResult] = []
        for analyzer in self._analyzers:
            name = analyzer.__class__.__name__
            print(f"  Running {name}...")
            results.append(analyzer.analyze(chat))

        # 3. Visualize
        print("  Generating charts...")
        chart_paths: dict[str, list[str]] = {}
        for result in results:
            if result.chart_data:
                paths = []
                for chart_id, chart_spec in result.chart_data.items():
                    path = self._visualizer.create_chart(
                        chart_type=chart_spec["type"],
                        data=chart_spec["data"],
                        title=chart_spec["title"],
                        **chart_spec.get("kwargs", {}),
                    )
                    if path:
                        paths.append(path)
                chart_paths[result.section_id] = paths

        # 4. Generate report
        print("  Assembling report...")
        metadata = {
            "participants": chat.participants,
            "source_file": chat.source_file,
            "date_range": chat.date_range,
        }
        return self._report_generator.generate(results, chart_paths, metadata)
