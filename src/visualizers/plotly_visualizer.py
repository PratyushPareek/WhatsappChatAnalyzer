import plotly.graph_objects as go

from src.visualizers.base import IVisualizer

# Design system participant colors
_PERSON_COLORS = [
    "#D94F30",  # vermillion
    "#2A7B9B",  # teal
    "#7B6DAA",  # muted plum
    "#D4A843",  # golden
    "#2D8B55",  # forest
]
_ACCENT = "#D94F30"
_ACCENT_MUTED = "#E8836C"
_TEXT = "#2C2A28"
_TEXT_MUTED = "#9E9790"
_BORDER_LIGHT = "#EEEBE5"
_BG = "#FAF7F2"
_SURFACE = "#FFFFFF"


class PlotlyVisualizer(IVisualizer):
    """Generates Plotly chart HTML fragments (not files). Returns an HTML div string."""

    def __init__(self, style: dict | None = None):
        self._style = style or {}
        self._colors = _PERSON_COLORS

    def create_chart(self, chart_type: str, data: dict, title: str, **kwargs) -> str:
        method = getattr(self, f"_{chart_type}", None)
        if method is None:
            raise ValueError(f"Unknown chart type: {chart_type}")
        return method(data, title, **kwargs)

    def _base_layout(self, title: str, **kwargs) -> dict:
        return dict(
            title=dict(text=title, font=dict(family="Bricolage Grotesque, Georgia, serif", size=18, color=_TEXT)),
            xaxis_title=dict(text=kwargs.get("xlabel", ""), font=dict(family="DM Sans, sans-serif", size=13, color=_TEXT_MUTED)),
            yaxis_title=dict(text=kwargs.get("ylabel", ""), font=dict(family="DM Sans, sans-serif", size=13, color=_TEXT_MUTED)),
            xaxis=dict(gridcolor=_BORDER_LIGHT, linecolor=_BORDER_LIGHT, tickfont=dict(family="DM Sans, sans-serif", size=11, color=_TEXT_MUTED)),
            yaxis=dict(gridcolor=_BORDER_LIGHT, linecolor=_BORDER_LIGHT, tickfont=dict(family="DM Sans, sans-serif", size=11, color=_TEXT_MUTED)),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            height=400,
            margin=dict(l=60, r=30, t=60, b=60),
            hoverlabel=dict(bgcolor=_SURFACE, font_color=_TEXT, bordercolor=_BORDER_LIGHT),
        )

    def _line(self, data: dict, title: str, **kwargs) -> str:
        keys = list(data.keys())
        values = list(data.values())
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=keys, y=values, mode="lines",
            line=dict(color=_ACCENT, width=2.5, shape="spline"),
            fill="tozeroy",
            fillcolor=f"rgba({self._hex_to_rgb(_ACCENT)}, 0.06)",
        ))
        fig.update_layout(**self._base_layout(title, **kwargs))
        return fig.to_html(full_html=False, include_plotlyjs=False)

    def _bar(self, data: dict, title: str, **kwargs) -> str:
        keys = [str(k) for k in data.keys()]
        values = list(data.values())
        colors = [self._colors[i % len(self._colors)] for i in range(len(keys))]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=keys, y=values,
            marker_color=colors,
            marker_line=dict(width=0),
        ))
        layout = self._base_layout(title, **kwargs)
        layout["bargap"] = 0.3
        fig.update_layout(**layout)
        return fig.to_html(full_html=False, include_plotlyjs=False)

    def _wordcloud(self, data: dict, title: str, **kwargs) -> str:
        if not data:
            return ""
        sorted_words = sorted(data.items(), key=lambda x: x[1], reverse=True)[:50]
        max_count = sorted_words[0][1] if sorted_words else 1

        words_html = []
        for word, count in sorted_words:
            size = max(14, int(14 + 36 * (count / max_count)))
            opacity = max(0.5, count / max_count)
            color_idx = hash(word) % len(self._colors)
            words_html.append(
                f'<span style="font-size:{size}px; color:{self._colors[color_idx]}; '
                f'opacity:{opacity:.2f}; padding:4px 8px; display:inline-block; '
                f'font-family: DM Sans, sans-serif;">{word}</span>'
            )

        return (
            f'<div class="wordcloud-box">'
            f'<div class="wordcloud-title">{title}</div>'
            f'<div class="wordcloud-words">{"".join(words_html)}</div>'
            f'</div>'
        )

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> str:
        hex_color = hex_color.lstrip("#")
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return f"{r}, {g}, {b}"
