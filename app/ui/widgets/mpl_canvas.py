"""
Matplotlib chart widget for embedding charts in PySide6 layouts.
"""

from __future__ import annotations

import matplotlib
matplotlib.use("QtAgg")

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from app.constants import CHART_COLORS

# RTL support for Persian text
plt.rcParams["font.family"] = "Tahoma"
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 100


class MplCanvas(QWidget):
    """Reusable Matplotlib canvas embedded in a QWidget."""

    def __init__(self, parent=None, width: int = 6, height: int = 4, dpi: int = 100):
        super().__init__(parent)
        self.fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

    def clear(self) -> None:
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        self.canvas.draw()

    def draw_bar(self, title: str, labels: list[str], values: list[float], ylabel: str = "") -> None:
        self.clear()
        self.ax.bar(labels, values, color=CHART_COLORS[: len(labels)], edgecolor="white", linewidth=0.5)
        self.ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
        self.ax.set_ylabel(ylabel, fontsize=10)
        self.ax.tick_params(axis="x", rotation=30)
        self.fig.tight_layout()
        self.canvas.draw()

    def draw_horizontal_bar(self, title: str, labels: list[str], values: list[float], ylabel: str = "") -> None:
        self.clear()
        colors = CHART_COLORS[: len(labels)]
        self.ax.barh(labels, values, color=colors, edgecolor="white", height=0.6)
        self.ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
        self.ax.set_xlabel(ylabel, fontsize=10)
        self.fig.tight_layout()
        self.canvas.draw()

    def draw_pie(self, title: str, labels: list[str], values: list[float]) -> None:
        self.clear()
        if not values or all(v == 0 for v in values):
            self.ax.text(0.5, 0.5, "داده‌ای موجود نیست", ha="center", va="center", fontsize=14)
            self.canvas.draw()
            return
        colors = CHART_COLORS[: len(labels)]
        wedges, texts, autotexts = self.ax.pie(
            values, labels=labels, autopct="%1.1f%%",
            colors=colors, startangle=90, pctdistance=0.85,
        )
        for t in autotexts:
            t.set_fontsize(9)
        self.ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
        self.fig.tight_layout()
        self.canvas.draw()

    def draw_line(self, title: str, labels: list[str], values: list[float], ylabel: str = "") -> None:
        self.clear()
        x = list(range(len(labels)))
        self.ax.plot(x, values, marker="o", color=CHART_COLORS[0], linewidth=2, markersize=6)
        self.ax.fill_between(x, values, alpha=0.1, color=CHART_COLORS[0])
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(labels)
        self.ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
        self.ax.set_ylabel(ylabel, fontsize=10)
        self.ax.tick_params(axis="x", rotation=30)
        self.ax.grid(True, alpha=0.3)
        self.fig.tight_layout()
        self.canvas.draw()

    def draw_grouped_bar(self, title: str, labels: list[str], series: dict[str, list[float]], ylabel: str = "") -> None:
        """Grouped bar chart for comparing multiple series."""
        self.clear()
        import numpy as np
        x = np.arange(len(labels))
        n = len(series)
        width = 0.7 / max(n, 1)
        for i, (name, values) in enumerate(series.items()):
            self.ax.bar(x + i * width - (n - 1) * width / 2, values, width, label=name, color=CHART_COLORS[i])
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(labels)
        self.ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
        self.ax.set_ylabel(ylabel, fontsize=10)
        self.ax.legend(fontsize=9)
        self.ax.tick_params(axis="x", rotation=30)
        self.fig.tight_layout()
        self.canvas.draw()

    def draw_histogram(self, title: str, data: list[float], bins: int = 10, xlabel: str = "", ylabel: str = "") -> None:
        self.clear()
        if not data:
            self.ax.text(0.5, 0.5, "داده‌ای موجود نیست", ha="center", va="center", fontsize=14)
            self.canvas.draw()
            return
        self.ax.hist(data, bins=bins, color=CHART_COLORS[0], edgecolor="white", alpha=0.8)
        self.ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
        self.ax.set_xlabel(xlabel, fontsize=10)
        self.ax.set_ylabel(ylabel, fontsize=10)
        self.ax.grid(True, alpha=0.3, axis="y")
        self.fig.tight_layout()
        self.canvas.draw()

    def draw_box_plot(self, title: str, data: dict[str, list[float]]) -> None:
        self.clear()
        if not data:
            self.ax.text(0.5, 0.5, "داده‌ای موجود نیست", ha="center", va="center", fontsize=14)
            self.canvas.draw()
            return
        labels = list(data.keys())
        values = [v for v in data.values() if v]
        if not values:
            self.ax.text(0.5, 0.5, "داده‌ای موجود نیست", ha="center", va="center", fontsize=14)
            self.canvas.draw()
            return
        bp = self.ax.boxplot(values, labels=labels, patch_artist=True)
        for patch, color in zip(bp["boxes"], CHART_COLORS):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        self.ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
        self.ax.tick_params(axis="x", rotation=30)
        self.fig.tight_layout()
        self.canvas.draw()
