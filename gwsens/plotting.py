"""Core data loading and plotting utilities for GWSens.

The functions in this module are framework-agnostic, so the same plot used by
the Streamlit app can be reproduced from a notebook or script.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import io
import os
from pathlib import Path
from typing import Mapping

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp")

import matplotlib
matplotlib.use("Agg")
import matplotlib.colors as mcolors
import matplotlib.patheffects as PathEffects
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Polygon
from matplotlib.ticker import FuncFormatter
import numpy as np

from config import (
    AXIS_DEFAULTS,
    DATA_DIR_DETECTORS,
    DATA_DIR_SOURCES,
    DETECTORS,
    PLOT_DEFAULTS,
    SOURCES,
    THEME_SETTINGS,
    get_default_detectors,
    get_default_sources,
)

PLOT_TYPES = {1: "Characteristic Strain", 0: "Power Spectral Density"}
H0_HZ = 3.240779291010696e-18


@dataclass(frozen=True)
class PlotSettings:
    """User-facing plot options shared by Streamlit and notebooks."""

    plot_type: int = 1
    detectors: tuple[str, ...] = tuple(get_default_detectors())
    sources: tuple[str, ...] = tuple(get_default_sources())
    theme: str = "Light"
    figsize: tuple[float, float] = PLOT_DEFAULTS["figsize"]
    dpi: int = PLOT_DEFAULTS["dpi"]
    x_min: float = AXIS_DEFAULTS["x_min"]
    x_max: float = AXIS_DEFAULTS["x_max"]
    y_min: float = AXIS_DEFAULTS["y_min"]
    y_max: float = AXIS_DEFAULTS["y_max"]
    line_width: float = 1.5
    label_fontsize: int = PLOT_DEFAULTS["label_fontsize"]
    axis_fontsize: int = 10
    label_stroke: int | None = None
    label_color: str | None = None
    grid_color: str | None = None
    use_latex: bool = False
    use_bold: bool = False
    font_family: str | None = None
    plot_credit: str = "streamlit/GWSens and references therein"
    source_fill: str = "gradient"


@lru_cache(maxsize=None)
def load_detector_data(key: str) -> np.ndarray:
    """Load detector curve data as ``[frequency, strain]`` rows."""

    return _load_csv(Path(DATA_DIR_DETECTORS) / DETECTORS[key]["file"])


@lru_cache(maxsize=None)
def load_source_data(key: str) -> np.ndarray:
    """Load source curve data as ``[frequency, strain]`` rows."""

    return _load_csv(Path(DATA_DIR_SOURCES) / SOURCES[key]["file"])


def _load_csv(path: Path) -> np.ndarray:
    data = np.loadtxt(path, delimiter=",", skiprows=1)
    return np.atleast_2d(data)


def curve_to_log_plot(data: np.ndarray, plot_type: int) -> tuple[np.ndarray, np.ndarray]:
    """Convert ``[frequency, strain]`` data to log10 plot coordinates."""

    frequency = data[:, 0]
    strain = data[:, 1]
    x = np.log10(frequency)
    if plot_type == 1:
        return x, np.log10(strain)
    omega_gw = 2 * (np.pi * strain * frequency / H0_HZ) ** 2
    return x, np.log10(omega_gw)


def create_plot(
    settings: PlotSettings | None = None,
    detector_overrides: Mapping[str, Mapping[str, object]] | None = None,
    source_overrides: Mapping[str, Mapping[str, object]] | None = None,
) -> tuple[Figure, Axes]:
    """Create a GWSens matplotlib figure.

    Example
    -------
    ``fig, ax = create_plot(PlotSettings(sources=("GW150914", "GW230814")))``
    """

    settings = settings or PlotSettings()
    detector_overrides = detector_overrides or {}
    source_overrides = source_overrides or {}
    theme_cfg = THEME_SETTINGS[settings.theme]
    label_stroke = _coalesce(settings.label_stroke, theme_cfg["label_linewidth"])
    label_color = _coalesce(settings.label_color, theme_cfg["label_color"])
    grid_color = _coalesce(
        settings.grid_color,
        "#808080" if settings.theme == "Light" else "#404040",
    )
    fig_bg = "white" if settings.theme == "Light" else "#0e1117"

    with plt.style.context(theme_cfg["style"]):
        _configure_fonts(settings.use_latex, settings.font_family)
        fig, ax = plt.subplots(
            figsize=settings.figsize,
            dpi=settings.dpi,
            facecolor=fig_bg,
        )
        ax.set_facecolor(fig_bg)

        for key in settings.detectors:
            _plot_detector(
                ax,
                key,
                settings,
                theme_cfg["detector_color"],
                detector_overrides.get(key, {}),
                label_stroke,
                label_color,
            )

        for key in settings.sources:
            _plot_source(
                ax,
                key,
                settings,
                source_overrides.get(key, {}),
                label_stroke,
                label_color,
            )

        _configure_axes(ax, settings, grid_color)
        if settings.plot_credit:
            credit_color = "#666666" if settings.theme == "Light" else "#aaaaaa"
            credit = ax.text(
                1.0,
                -0.08,
                settings.plot_credit,
                ha="right",
                va="top",
                fontsize=8,
                color=credit_color,
                transform=ax.transAxes,
            )
            credit.set_gid("gwsens_font_text")
        try:
            fig.tight_layout()
        except ValueError:
            pass
        return fig, ax


def save_figure(fig: Figure, fmt: str, facecolor: str = "white") -> bytes:
    """Return a saved figure as bytes for downloads or notebooks."""

    buf = io.BytesIO()
    fig.savefig(
        buf,
        format=fmt,
        facecolor=facecolor,
        edgecolor="none",
        bbox_inches="tight",
    )
    buf.seek(0)
    return buf.getvalue()


def gradient_fill(
    ax: Axes,
    x: np.ndarray,
    y: np.ndarray,
    fill_color: str,
    ymin: float,
    alpha: float = PLOT_DEFAULTS["gradient_alpha"],
):
    """Plot a clipped vertical alpha gradient beneath a curve."""

    z = np.empty((100, 1, 4), dtype=float)
    z[:, :, :3] = mcolors.to_rgb(fill_color)
    z[:, :, -1] = np.linspace(0, alpha, 100)[:, None]
    image = ax.imshow(
        z,
        aspect="auto",
        extent=[x.min(), x.max(), ymin, y.max()],
        origin="lower",
    )
    xy = np.vstack(
        [[x.min(), ymin], np.column_stack([x, y]), [x.max(), ymin], [x.min(), ymin]]
    )
    clip_path = Polygon(xy, facecolor="none", edgecolor="none", closed=True)
    ax.add_patch(clip_path)
    image.set_clip_path(clip_path)
    ax.autoscale(True)
    return image


def format_label(label: str, use_latex: bool, use_bold: bool) -> str:
    """Format a label for optional LaTeX rendering."""

    if not use_latex:
        return label
    label = label.replace("_", r"\_")
    lines = label.split("\n")
    if use_bold:
        return "\n".join(rf"\textbf{{{line}}}" for line in lines)
    return "\n".join(lines)


def _plot_detector(
    ax: Axes,
    key: str,
    settings: PlotSettings,
    default_color: str,
    overrides: Mapping[str, object],
    label_stroke: int,
    label_color: str,
) -> None:
    det = DETECTORS[key]
    x, y = curve_to_log_plot(load_detector_data(key), settings.plot_type)
    color = _override(overrides, "color", default_color)
    label = _override(overrides, "label", det["label"])
    lx = _override(overrides, "label_x", det["label_x"])
    ly = _override(overrides, "label_y", det["label_y"])

    ax.plot(x, y, color=color, linewidth=settings.line_width)
    _add_label(ax, label, lx, ly, color, settings, label_stroke, label_color)


def _plot_source(
    ax: Axes,
    key: str,
    settings: PlotSettings,
    overrides: Mapping[str, object],
    label_stroke: int,
    label_color: str,
) -> None:
    src = SOURCES[key]
    x, y = curve_to_log_plot(load_source_data(key), settings.plot_type)
    color = _override(overrides, "color", src["color"])
    label = _override(overrides, "label", src["label"])
    lx = _override(overrides, "label_x", src["label_x"])
    ly = _override(overrides, "label_y", src["label_y"])

    y_floor = np.log10(settings.y_min)
    if settings.source_fill == "solid":
        ax.fill_between(x, y_floor, y, color=color, alpha=0.35, linewidth=0)
    else:
        gradient_fill(ax, x, y, color, y_floor)
    _add_label(ax, label, lx, ly, color, settings, label_stroke, label_color)


def _add_label(
    ax: Axes,
    label: str,
    x: float,
    y: float,
    color: str,
    settings: PlotSettings,
    label_stroke: int,
    label_color: str,
) -> None:
    fontweight = "bold" if settings.use_bold else "normal"
    text = ax.text(
        np.log10(x),
        np.log10(y),
        format_label(label, settings.use_latex, settings.use_bold),
        fontsize=settings.label_fontsize,
        fontweight=fontweight,
        ha="left",
        color=color,
    )
    text.set_gid("gwsens_font_text")
    text.set_path_effects(
        [PathEffects.withStroke(linewidth=label_stroke, foreground=label_color)]
    )


def _configure_axes(ax: Axes, settings: PlotSettings, grid_color: str) -> None:
    ax.grid(
        True,
        which="both",
        ls=PLOT_DEFAULTS["grid_linestyle"],
        linewidth=PLOT_DEFAULTS["grid_linewidth"],
        alpha=PLOT_DEFAULTS["grid_alpha"],
        color=grid_color,
        zorder=0,
    )
    xlabel = ax.set_xlabel("Frequency (Hz)", fontsize=settings.axis_fontsize)
    ylabel = ax.set_ylabel(PLOT_TYPES[settings.plot_type], fontsize=settings.axis_fontsize)
    xlabel.set_gid("gwsens_font_text")
    ylabel.set_gid("gwsens_font_text")
    ax.set_xlim(np.log10(settings.x_min), np.log10(settings.x_max))
    ax.set_ylim(np.log10(settings.y_min), np.log10(settings.y_max))
    ax.tick_params(labelsize=settings.axis_fontsize - 2)
    ax.xaxis.set_major_formatter(FuncFormatter(power_of_10_formatter))
    ax.yaxis.set_major_formatter(FuncFormatter(power_of_10_formatter))


def _configure_fonts(use_latex: bool, font_family: str | None = None) -> None:
    matplotlib.rcParams["text.usetex"] = use_latex
    if use_latex:
        matplotlib.rcParams["font.family"] = "serif"
        matplotlib.rcParams["font.serif"] = ["Computer Modern Roman"]
    elif font_family:
        matplotlib.rcParams["font.family"] = font_family
    else:
        matplotlib.rcParams["font.family"] = "sans-serif"


def power_of_10_formatter(x: float, _pos: int) -> str:
    """Format log-axis tick labels as powers of 10."""

    return f"$10^{{{int(x)}}}$"


def _override(overrides: Mapping[str, object], field: str, default):
    return overrides.get(field, default)


def _coalesce(value, default):
    return default if value is None else value
