"""GWSens - Gravitational Wave Sensitivity Curve Visualizer"""

import io
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patheffects as PathEffects
from matplotlib.patches import Polygon
from matplotlib.ticker import FuncFormatter
import numpy as np
import streamlit as st

from config import (
    DATA_DIR_DETECTORS, DATA_DIR_SOURCES, AXIS_DEFAULTS, THEME_SETTINGS,
    DETECTORS, SOURCES, get_default_detectors, get_default_sources,
    get_detector_references, get_source_references,
)

# =============================================================================
# PAGE CONFIG & CONSTANTS
# =============================================================================
st.set_page_config(page_title="GWSens", page_icon=":dizzy:", layout="wide")
PLOT_TYPES = {1: "Characteristic Strain", 0: "Power Spectral Density"}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def gradient_fill(x, y, fill_color, ymin, ax, alpha=0.8):
    """Plot gradient-filled area beneath a curve."""
    z = np.empty((100, 1, 4), dtype=float)
    z[:, :, :3] = mcolors.to_rgb(fill_color)
    z[:, :, -1] = np.linspace(0, alpha, 100)[:, None]
    im = ax.imshow(z, aspect="auto", extent=[x.min(), x.max(), ymin, y.max()], origin="lower")
    xy = np.vstack([[x.min(), ymin], np.column_stack([x, y]), [x.max(), ymin], [x.min(), ymin]])
    clip_path = Polygon(xy, facecolor="none", edgecolor="none", closed=True)
    ax.add_patch(clip_path)
    im.set_clip_path(clip_path)
    ax.autoscale(True)
    return im

def data_to_plot(data, plot_type):
    """Transform data for plotting (returns log10 values)."""
    x = np.log10(data[:, 0])
    if plot_type == 1:
        return x, np.log10(data[:, 1])
    H0 = 3.240779291010696e-18
    return x, np.log10(2 * (np.pi * data[:, 1] * data[:, 0] / H0) ** 2)

def save_figure(fig, fmt, facecolor):
    """Save figure to bytes buffer."""
    buf = io.BytesIO()
    fig.savefig(buf, format=fmt, facecolor=facecolor, edgecolor='none', bbox_inches="tight")
    buf.seek(0)
    return buf.getvalue()

def format_label(label, use_latex, use_bold):
    """Format label for display, optionally bold."""
    if use_latex:
        # Escape special LaTeX characters
        label = label.replace("_", r"\_")
        lines = label.split("\n")
        if use_bold:
            return "\n".join(rf"\textbf{{{line}}}" for line in lines)
        return "\n".join(lines)
    return label

@st.cache_data
def load_detector_data(key):
    return np.loadtxt(Path(DATA_DIR_DETECTORS) / DETECTORS[key]["file"], delimiter=",", skiprows=1)

@st.cache_data
def load_source_data(key):
    return np.loadtxt(Path(DATA_DIR_SOURCES) / SOURCES[key]["file"], delimiter=",", skiprows=1)

# =============================================================================
# SESSION STATE
# =============================================================================
if "detector_overrides" not in st.session_state:
    st.session_state.detector_overrides = {}
if "source_overrides" not in st.session_state:
    st.session_state.source_overrides = {}
if "last_theme" not in st.session_state:
    st.session_state.last_theme = "Light"

def get_override(cat, key, field, default):
    return st.session_state.get(f"{cat}_overrides", {}).get(key, {}).get(field, default)

def set_override(cat, key, field, value):
    st.session_state.setdefault(f"{cat}_overrides", {}).setdefault(key, {})[field] = value

# =============================================================================
# SIDEBAR
# =============================================================================
st.sidebar.title("GWSens")
st.sidebar.caption("Gravitational Wave Sensitivity Curve Plotter")

# Plot type
plot_type = st.sidebar.radio("Plot type:", list(PLOT_TYPES.keys()), format_func=lambda x: PLOT_TYPES[x])

# Selections
det_labels = {k: DETECTORS[k]["label"] for k in DETECTORS}
selected_det = st.sidebar.multiselect("Sensitivity curves", list(DETECTORS.keys()),
                                       default=get_default_detectors(), format_func=lambda x: det_labels[x])
selected_src = st.sidebar.multiselect("Sources", list(SOURCES.keys()), default=get_default_sources())

# Theme
theme = st.sidebar.selectbox("Theme", list(THEME_SETTINGS.keys()))
theme_cfg = THEME_SETTINGS[theme]

# Reset color overrides when theme changes
if theme != st.session_state.last_theme:
    for key in st.session_state.detector_overrides:
        st.session_state.detector_overrides[key].pop("color", None)
    st.session_state.last_theme = theme

# LaTeX and bold
c1, c2 = st.sidebar.columns(2)
use_latex = c1.checkbox("LaTeX", value=False, help="Requires LaTeX installation")
use_bold = c2.checkbox("Bold labels", value=False)
plt.style.use(theme_cfg["style"])
matplotlib.rcParams["text.usetex"] = use_latex
if use_latex:
    matplotlib.rcParams["font.family"] = "serif"
    matplotlib.rcParams["font.serif"] = ["Computer Modern Roman"]
else:
    matplotlib.rcParams["font.family"] = "sans-serif"

# Figure size
st.sidebar.write("**Figure Size**")
c1, c2 = st.sidebar.columns(2)
fig_width = c1.number_input("Width", 4.0, 20.0, 7.0, step=0.5)
fig_height = c2.number_input("Height", 3.0, 15.0, 4.5, step=0.5)
fig_dpi = st.sidebar.number_input("DPI", 72, 600, 300, step=50)

# Axis limits
st.sidebar.write("**Axis Limits**")
c1, c2 = st.sidebar.columns(2)
x_min = c1.number_input("$x_{min}$", format="%.1e", value=AXIS_DEFAULTS["x_min"])
y_min = c1.number_input("$y_{min}$", format="%.1e", value=AXIS_DEFAULTS["y_min"])
x_max = c2.number_input("$x_{max}$", format="%.1e", value=AXIS_DEFAULTS["x_max"])
y_max = c2.number_input("$y_{max}$", format="%.1e", value=AXIS_DEFAULTS["y_max"])

# Styling
st.sidebar.write("**Styling**")
c1, c2 = st.sidebar.columns(2)
line_width = c1.slider("Line width", 0.5, 5.0, 1.5, 0.5)
label_fontsize = c1.slider("Label font", 6, 16, 8)
axis_fontsize = c2.slider("Axis font", 8, 18, 10)
label_stroke = c2.slider("Label stroke", 0, 5, theme_cfg["label_linewidth"])
c1, c2 = st.sidebar.columns(2)
label_color = c1.color_picker("Stroke color", theme_cfg["label_color"])
grid_color = c2.color_picker("Grid color", "#808080" if theme == "Light" else "#404040")

# Plot credit/watermark
plot_credit = st.sidebar.text_input("Plot credit", value="streamlit/GWSens and references therein")

# Advanced settings
st.sidebar.subheader("Advanced Settings")
adv_type = st.sidebar.selectbox("Edit", ["Sensitivity curve", "Source"])

if adv_type == "Sensitivity curve" and selected_det:
    adv_key = st.sidebar.selectbox("Select curve", selected_det, format_func=lambda x: det_labels[x])
    det = DETECTORS[adv_key]
    c1, c2 = st.sidebar.columns(2)

    new_x = c1.number_input("$x_{label}$", format="%.1e",
                            value=get_override("detector", adv_key, "label_x", det["label_x"]), key=f"dx_{adv_key}")
    set_override("detector", adv_key, "label_x", new_x)

    variants = det.get("variants", [])
    if variants:
        opts = [det["label"]] + variants
        cur = get_override("detector", adv_key, "label", det["label"])
        if cur not in opts: opts.append(cur)
        new_label = c1.selectbox("Label", opts, index=opts.index(cur) if cur in opts else 0, key=f"dl_{adv_key}")
    else:
        new_label = c1.text_input("Label", get_override("detector", adv_key, "label", det["label"]), key=f"dl_{adv_key}")
    set_override("detector", adv_key, "label", new_label)

    new_y = c2.number_input("$y_{label}$", format="%.1e",
                            value=get_override("detector", adv_key, "label_y", det["label_y"]), key=f"dy_{adv_key}")
    set_override("detector", adv_key, "label_y", new_y)

    new_color = c2.color_picker("Color", get_override("detector", adv_key, "color", theme_cfg["detector_color"]), key=f"dc_{adv_key}")
    set_override("detector", adv_key, "color", new_color)

elif adv_type == "Source" and selected_src:
    adv_key = st.sidebar.selectbox("Select source", selected_src)
    src = SOURCES[adv_key]
    c1, c2 = st.sidebar.columns(2)

    new_x = c1.number_input("$x_{label}$", format="%.1e",
                            value=get_override("source", adv_key, "label_x", src["label_x"]), key=f"sx_{adv_key}")
    set_override("source", adv_key, "label_x", new_x)

    new_label = c1.text_input("Label", get_override("source", adv_key, "label", src["label"]), key=f"sl_{adv_key}")
    set_override("source", adv_key, "label", new_label)

    new_y = c2.number_input("$y_{label}$", format="%.1e",
                            value=get_override("source", adv_key, "label_y", src["label_y"]), key=f"sy_{adv_key}")
    set_override("source", adv_key, "label_y", new_y)

    new_color = c2.color_picker("Color", get_override("source", adv_key, "color", src["color"]), key=f"sc_{adv_key}")
    set_override("source", adv_key, "color", new_color)

if st.sidebar.button("Reset All"):
    st.session_state.detector_overrides = {}
    st.session_state.source_overrides = {}
    st.cache_data.clear()
    st.rerun()

# =============================================================================
# MAIN CONTENT
# =============================================================================

# Determine colors
fig_bg = "white" if theme == "Light" else "#0e1117"

# Create figure
fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=fig_dpi, facecolor=fig_bg)
ax.set_facecolor(fig_bg)

# Plot sensitivity curves
for key in selected_det:
    det = DETECTORS[key]
    x, y = data_to_plot(load_detector_data(key), plot_type)
    color = get_override("detector", key, "color", theme_cfg["detector_color"])
    label = get_override("detector", key, "label", det["label"])
    lx = get_override("detector", key, "label_x", det["label_x"])
    ly = get_override("detector", key, "label_y", det["label_y"])

    ax.plot(x, y, color=color, linewidth=line_width)
    display_label = format_label(label, use_latex, use_bold)
    fontweight = "bold" if use_bold else "normal"
    txt = ax.text(np.log10(lx), np.log10(ly), display_label, fontsize=label_fontsize, fontweight=fontweight, color=color)
    txt.set_path_effects([PathEffects.withStroke(linewidth=label_stroke, foreground=label_color)])

# Plot sources
for key in selected_src:
    src = SOURCES[key]
    x, y = data_to_plot(load_source_data(key), plot_type)
    color = get_override("source", key, "color", src["color"])
    label = get_override("source", key, "label", src["label"])
    lx = get_override("source", key, "label_x", src["label_x"])
    ly = get_override("source", key, "label_y", src["label_y"])

    gradient_fill(x, y, color, np.log10(y_min), ax)
    display_label = format_label(label, use_latex, use_bold)
    fontweight = "bold" if use_bold else "normal"
    txt = ax.text(np.log10(lx), np.log10(ly), display_label, fontsize=label_fontsize, fontweight=fontweight, ha="left", color=color)
    txt.set_path_effects([PathEffects.withStroke(linewidth=label_stroke, foreground=label_color)])

# Configure axes
ax.grid(True, which="both", ls="dotted", linewidth=0.8, alpha=0.8, color=grid_color, zorder=0)
ax.set_xlabel("Frequency (Hz)", fontsize=axis_fontsize)
ax.set_ylabel(PLOT_TYPES[plot_type], fontsize=axis_fontsize)
ax.set_xlim(np.log10(x_min), np.log10(x_max))
ax.set_ylim(np.log10(y_min), np.log10(y_max))
ax.tick_params(labelsize=axis_fontsize - 2)

def power_of_10_formatter(x, pos):
    """Format tick as 10^x without mathtext issues."""
    exp = int(x)
    return f"$10^{{{exp}}}$"

ax.xaxis.set_major_formatter(FuncFormatter(power_of_10_formatter))
ax.yaxis.set_major_formatter(FuncFormatter(power_of_10_formatter))

# Add plot credit aligned with axis right edge
if plot_credit:
    credit_color = "#666666" if theme == "Light" else "#aaaaaa"
    ax.text(1.0, -0.08, plot_credit, ha='right', va='top', fontsize=8,
            color=credit_color, transform=ax.transAxes)

try:
    plt.tight_layout()
except ValueError:
    pass  # Skip tight_layout if it fails - not critical

# Display plot - wrap in try/except for robustness
try:
    st.pyplot(fig, use_container_width=True)
except ValueError:
    # Fallback: save to buffer and display as image
    buf = io.BytesIO()
    fig.savefig(buf, format='png', facecolor=fig_bg, dpi=150)
    buf.seek(0)
    st.image(buf, use_container_width=True)

# Download buttons (below figure)
st.write("**Download:**")
c1, c2, c3, c4 = st.columns(4)
try:
    c1.download_button("PNG", save_figure(fig, "png", fig_bg), "gwsens.png", "image/png")
    c2.download_button("PDF", save_figure(fig, "pdf", fig_bg), "gwsens.pdf", "application/pdf")
    c3.download_button("SVG", save_figure(fig, "svg", fig_bg), "gwsens.svg", "image/svg+xml")
    c4.download_button("JPEG", save_figure(fig, "jpeg", "white"), "gwsens.jpg", "image/jpeg")
except ValueError:
    st.caption("Downloads temporarily unavailable - adjust a setting to refresh")

plt.close(fig)

# =============================================================================
# REFERENCES
# =============================================================================
st.divider()
st.subheader("References")

det_refs = get_detector_references(selected_det)
src_refs = get_source_references(selected_src)

if det_refs or src_refs:
    if det_refs:
        st.write("**Sensitivity curves:**")
        for r in det_refs:
            link = f" — [link]({r['url']})" if r["url"] else ""
            st.markdown(f"- **{r['name']}**: {r['reference']}{link}")
    if src_refs:
        st.write("**Sources:**")
        for r in src_refs:
            link = f" — [link]({r['url']})" if r["url"] else ""
            st.markdown(f"- **{r['name']}**: {r['reference']}{link}")
else:
    st.info("Select sensitivity curves or sources to see their references.")

st.divider()
st.caption("Developed by N. Borghi | Made with [Streamlit](https://streamlit.io/) | Inspired by [gwplotter.com](http://gwplotter.com/)")
