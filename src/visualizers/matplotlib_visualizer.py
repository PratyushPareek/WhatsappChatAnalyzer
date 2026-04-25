import os
import uuid
from pathlib import Path

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from wordcloud import WordCloud
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from src.visualizers.base import IVisualizer


class MatplotlibVisualizer(IVisualizer):
    def __init__(self, output_dir: str, style: dict | None = None):
        self._output_dir = output_dir
        self._style = style or {}
        self._available = MATPLOTLIB_AVAILABLE
        if self._available:
            Path(self._output_dir).mkdir(parents=True, exist_ok=True)
        else:
            print("  Warning: matplotlib unavailable (DLL blocked). Charts will be skipped.")

    def create_chart(self, chart_type: str, data: dict, title: str, **kwargs) -> str:
        if not self._available:
            return ""
        method = getattr(self, f"_{chart_type}", None)
        if method is None:
            raise ValueError(f"Unknown chart type: {chart_type}")
        return method(data, title, **kwargs)

    def _line(self, data: dict, title: str, **kwargs) -> str:
        fig, ax = plt.subplots(figsize=(
            self._style.get("figure_width", 10),
            self._style.get("figure_height", 6),
        ))
        colors = self._style.get("color_palette", ["#4C72B0"])
        keys = list(data.keys())
        values = list(data.values())
        ax.plot(range(len(keys)), values, color=colors[0], linewidth=1.5)

        # Thin out x-tick labels for readability
        if len(keys) > 20:
            step = max(1, len(keys) // 10)
            tick_positions = list(range(0, len(keys), step))
            ax.set_xticks(tick_positions)
            ax.set_xticklabels([keys[i] for i in tick_positions], rotation=45, ha="right", fontsize=8)
        else:
            ax.set_xticks(range(len(keys)))
            ax.set_xticklabels(keys, rotation=45, ha="right", fontsize=8)

        ax.set_title(title, fontsize=self._style.get("title_size", 14), fontweight="bold")
        ax.set_xlabel(kwargs.get("xlabel", ""), fontsize=self._style.get("font_size", 12))
        ax.set_ylabel(kwargs.get("ylabel", ""), fontsize=self._style.get("font_size", 12))
        ax.grid(axis="y", alpha=0.3)
        fig.tight_layout()
        return self._save(fig, title)

    def _bar(self, data: dict, title: str, **kwargs) -> str:
        fig, ax = plt.subplots(figsize=(
            self._style.get("figure_width", 10),
            self._style.get("figure_height", 6),
        ))
        colors = self._style.get("color_palette", ["#4C72B0"])
        keys = list(data.keys())
        values = list(data.values())
        bar_colors = [colors[i % len(colors)] for i in range(len(keys))]
        ax.bar([str(k) for k in keys], values, color=bar_colors)
        ax.set_title(title, fontsize=self._style.get("title_size", 14), fontweight="bold")
        ax.set_xlabel(kwargs.get("xlabel", ""), fontsize=self._style.get("font_size", 12))
        ax.set_ylabel(kwargs.get("ylabel", ""), fontsize=self._style.get("font_size", 12))
        plt.xticks(rotation=45, ha="right", fontsize=9)
        ax.grid(axis="y", alpha=0.3)
        fig.tight_layout()
        return self._save(fig, title)

    def _wordcloud(self, data: dict, title: str, **kwargs) -> str:
        if not data:
            return ""
        fig, ax = plt.subplots(figsize=(
            self._style.get("figure_width", 10),
            self._style.get("figure_height", 6),
        ))
        wc = WordCloud(
            width=1000,
            height=600,
            background_color="white",
            colormap="viridis",
            max_words=50,
        ).generate_from_frequencies(data)
        ax.imshow(wc, interpolation="bilinear")
        ax.set_title(title, fontsize=self._style.get("title_size", 14), fontweight="bold")
        ax.axis("off")
        fig.tight_layout()
        return self._save(fig, title)

    def _save(self, fig: plt.Figure, title: str) -> str:
        safe_name = "".join(c if c.isalnum() or c in "-_ " else "" for c in title).strip().replace(" ", "_")
        filename = f"{safe_name}_{uuid.uuid4().hex[:6]}.png"
        path = os.path.join(self._output_dir, filename)
        fig.savefig(path, dpi=self._style.get("dpi", 150), bbox_inches="tight")
        plt.close(fig)
        return path
