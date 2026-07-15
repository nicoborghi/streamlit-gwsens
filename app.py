"""GWSens - Gravitational Wave Sensitivity Curve Visualizer."""

import io
import os
import re
from dataclasses import replace
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp")

from matplotlib import font_manager
import matplotlib.pyplot as plt
import streamlit as st

from config import (
    AXIS_DEFAULTS,
    DETECTORS,
    SOURCES,
    THEME_SETTINGS,
    get_default_detectors,
    get_default_sources,
    get_detector_references,
    get_source_references,
)
from gwsens import PLOT_TYPES, PlotSettings, create_plot, save_figure

st.set_page_config(page_title="GWSens", page_icon=":dizzy:", layout="wide")

GOOGLE_FONTS = [
    "Default",
    "Inter",
    "Roboto",
    "Lato",
    "Source Sans 3",
    "Merriweather",
    "Playfair Display",
    "Space Grotesk",
]
FONT_CACHE_DIR = Path("/tmp/gwsens-google-fonts")
GOOGLE_FONT_TTF_URLS = {
    "Inter": [
        "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf",
    ],
    "Roboto": [
        "https://raw.githubusercontent.com/google/fonts/main/ofl/roboto/Roboto%5Bwdth,wght%5D.ttf",
    ],
    "Lato": [
        "https://raw.githubusercontent.com/google/fonts/main/ofl/lato/Lato-Regular.ttf",
        "https://raw.githubusercontent.com/google/fonts/main/ofl/lato/Lato-Bold.ttf",
    ],
    "Source Sans 3": [
        "https://raw.githubusercontent.com/google/fonts/main/ofl/sourcesans3/SourceSans3%5Bwght%5D.ttf",
    ],
    "Merriweather": [
        "https://raw.githubusercontent.com/google/fonts/main/ofl/merriweather/Merriweather%5Bopsz,wdth,wght%5D.ttf",
    ],
    "Playfair Display": [
        "https://raw.githubusercontent.com/google/fonts/main/ofl/playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf",
    ],
    "Space Grotesk": [
        "https://raw.githubusercontent.com/google/fonts/main/ofl/spacegrotesk/SpaceGrotesk%5Bwght%5D.ttf",
    ],
}

def init_session_state() -> None:
    st.session_state.setdefault("detector_overrides", {})
    st.session_state.setdefault("source_overrides", {})
    st.session_state.setdefault("last_theme", "Light")


def get_override(cat: str, key: str, field: str, default):
    return st.session_state.get(f"{cat}_overrides", {}).get(key, {}).get(field, default)


def set_override(cat: str, key: str, field: str, value) -> None:
    st.session_state.setdefault(f"{cat}_overrides", {}).setdefault(key, {})[field] = value


@st.cache_resource(show_spinner=False)
def load_google_font(font_family: str) -> str | None:
    """Download and register a Google Font for Matplotlib path rendering."""

    if font_family == "Default":
        return None

    FONT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    font_urls = GOOGLE_FONT_TTF_URLS[font_family]
    loaded = False
    for index, font_url in enumerate(font_urls):
        suffix = Path(font_url).suffix or ".ttf"
        font_path = FONT_CACHE_DIR / f"{font_family.replace(' ', '_')}_{index}{suffix}"
        if not font_path.exists():
            font_path.write_bytes(urlopen(Request(font_url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20).read())
        try:
            font_manager.fontManager.addfont(str(font_path))
            loaded = True
        except RuntimeError:
            continue
    return font_family if loaded else None


def freeze_overrides(overrides: dict) -> tuple:
    return tuple(
        (key, tuple(sorted(values.items())))
        for key, values in sorted(overrides.items())
    )


def svg_preview_html(svg_bytes: bytes) -> str:
    svg = svg_bytes.decode("utf-8")
    svg = svg[svg.find("<svg") :]
    svg = re.sub(r"\s(width|height)=\"[^\"]*\"", "", svg, count=2)
    svg = svg.replace(
        "<svg ",
        '<svg style="display:block; width:100%; height:auto; overflow:visible;" ',
        1,
    )
    return f'<div style="width:100%; overflow:visible;">{svg}</div>'


def show_svg(svg_bytes: bytes) -> None:
    st.markdown(
        svg_preview_html(svg_bytes),
        unsafe_allow_html=True,
    )


def render_advanced_settings(selected_det: list[str], selected_src: list[str]) -> None:
    st.sidebar.subheader("Advanced Settings")
    adv_type = st.sidebar.selectbox("Edit", ["Sensitivity curve", "Source"])
    det_labels = {k: DETECTORS[k]["label"] for k in DETECTORS}

    if adv_type == "Sensitivity curve" and selected_det:
        adv_key = st.sidebar.selectbox(
            "Select curve",
            selected_det,
            format_func=lambda x: det_labels[x],
        )
        det = DETECTORS[adv_key]
        c1, c2 = st.sidebar.columns(2)
        set_override(
            "detector",
            adv_key,
            "label_x",
            c1.number_input(
                "$x_{label}$",
                format="%.1e",
                value=get_override("detector", adv_key, "label_x", det["label_x"]),
                key=f"dx_{adv_key}",
            ),
        )
        set_override(
            "detector",
            adv_key,
            "label_y",
            c2.number_input(
                "$y_{label}$",
                format="%.1e",
                value=get_override("detector", adv_key, "label_y", det["label_y"]),
                key=f"dy_{adv_key}",
            ),
        )
        variants = det.get("variants", [])
        current_label = get_override("detector", adv_key, "label", det["label"])
        if variants:
            options = [det["label"]] + variants
            if current_label not in options:
                options.append(current_label)
            label_value = c1.selectbox(
                "Label",
                options,
                index=options.index(current_label),
                key=f"dl_{adv_key}",
            )
        else:
            label_value = c1.text_input("Label", current_label, key=f"dl_{adv_key}")
        set_override("detector", adv_key, "label", label_value)
        set_override(
            "detector",
            adv_key,
            "color",
            c2.color_picker(
                "Color",
                get_override("detector", adv_key, "color", st.session_state.theme_cfg["detector_color"]),
                key=f"dc_{adv_key}",
            ),
        )

    elif adv_type == "Source" and selected_src:
        adv_key = st.sidebar.selectbox("Select source", selected_src)
        src = SOURCES[adv_key]
        c1, c2 = st.sidebar.columns(2)
        set_override(
            "source",
            adv_key,
            "label_x",
            c1.number_input(
                "$x_{label}$",
                format="%.1e",
                value=get_override("source", adv_key, "label_x", src["label_x"]),
                key=f"sx_{adv_key}",
            ),
        )
        set_override(
            "source",
            adv_key,
            "label_y",
            c2.number_input(
                "$y_{label}$",
                format="%.1e",
                value=get_override("source", adv_key, "label_y", src["label_y"]),
                key=f"sy_{adv_key}",
            ),
        )
        set_override(
            "source",
            adv_key,
            "label",
            c1.text_input(
                "Label",
                get_override("source", adv_key, "label", src["label"]),
                key=f"sl_{adv_key}",
            ),
        )
        set_override(
            "source",
            adv_key,
            "color",
            c2.color_picker(
                "Color",
                get_override("source", adv_key, "color", src["color"]),
                key=f"sc_{adv_key}",
            ),
        )


init_session_state()

st.sidebar.title("GWSens")
st.sidebar.caption("Gravitational Wave Sensitivity Curve Plotter")

plot_type = st.sidebar.radio(
    "Plot type:",
    list(PLOT_TYPES.keys()),
    format_func=lambda x: PLOT_TYPES[x],
)
det_labels = {k: DETECTORS[k]["label"] for k in DETECTORS}
selected_det = st.sidebar.multiselect(
    "Sensitivity curves",
    list(DETECTORS.keys()),
    default=get_default_detectors(),
    format_func=lambda x: det_labels[x],
)
selected_src = st.sidebar.multiselect(
    "Sources",
    list(SOURCES.keys()),
    default=get_default_sources(),
)

theme = st.sidebar.selectbox("Theme", list(THEME_SETTINGS.keys()))
theme_cfg = THEME_SETTINGS[theme]
st.session_state.theme_cfg = theme_cfg
if theme != st.session_state.last_theme:
    for key in st.session_state.detector_overrides:
        st.session_state.detector_overrides[key].pop("color", None)
    st.session_state.last_theme = theme

plot_font = st.sidebar.selectbox(
    "Plot font",
    GOOGLE_FONTS,
    help="Downloads the selected Google Font for Matplotlib-rendered plot labels. Math stays Matplotlib-rendered.",
)
try:
    plot_font_family = load_google_font(plot_font)
except (URLError, TimeoutError, OSError, RuntimeError) as exc:
    plot_font_family = None
    st.sidebar.warning(f"Could not load {plot_font}: {exc}")

c1, c2 = st.sidebar.columns(2)
use_latex = c1.checkbox("LaTeX", value=False, help="Requires LaTeX installation")
use_bold = c2.checkbox("Bold labels", value=False)

st.sidebar.write("**Figure Size**")
c1, c2 = st.sidebar.columns(2)
fig_width = c1.number_input("Width", 4.0, 20.0, 7.0, step=0.5)
fig_height = c2.number_input("Height", 3.0, 15.0, 4.5, step=0.5)
fig_dpi = st.sidebar.number_input("DPI", 72, 600, 300, step=50)

st.sidebar.write("**Axis Limits**")
c1, c2 = st.sidebar.columns(2)
x_min = c1.number_input("$x_{min}$", format="%.1e", value=AXIS_DEFAULTS["x_min"])
y_min = c1.number_input("$y_{min}$", format="%.1e", value=AXIS_DEFAULTS["y_min"])
x_max = c2.number_input("$x_{max}$", format="%.1e", value=AXIS_DEFAULTS["x_max"])
y_max = c2.number_input("$y_{max}$", format="%.1e", value=AXIS_DEFAULTS["y_max"])

st.sidebar.write("**Styling**")
c1, c2 = st.sidebar.columns(2)
line_width = c1.slider("Line width", 0.5, 5.0, 1.5, 0.5)
label_fontsize = c1.slider("Label font", 6, 16, 8)
axis_fontsize = c2.slider("Axis font", 8, 18, 10)
label_stroke = c2.slider("Label stroke", 0, 5, theme_cfg["label_linewidth"])
c1, c2 = st.sidebar.columns(2)
label_color = c1.color_picker("Stroke color", theme_cfg["label_color"])
grid_color = c2.color_picker("Grid color", "#808080" if theme == "Light" else "#404040")
plot_credit = st.sidebar.text_input(
    "Plot credit",
    value="streamlit/GWSens and references therein",
)

render_advanced_settings(selected_det, selected_src)

if st.sidebar.button("Reset All"):
    st.session_state.detector_overrides = {}
    st.session_state.source_overrides = {}
    st.rerun()

settings = PlotSettings(
    plot_type=plot_type,
    detectors=tuple(selected_det),
    sources=tuple(selected_src),
    theme=theme,
    figsize=(fig_width, fig_height),
    dpi=fig_dpi,
    x_min=x_min,
    x_max=x_max,
    y_min=y_min,
    y_max=y_max,
    line_width=line_width,
    label_fontsize=label_fontsize,
    axis_fontsize=axis_fontsize,
    label_stroke=label_stroke,
    label_color=label_color,
    grid_color=grid_color,
    use_latex=use_latex,
    use_bold=use_bold,
    font_family=plot_font_family,
    plot_credit=plot_credit,
)
preview_settings = replace(
    settings,
    dpi=min(fig_dpi, 150),
)
fig, ax = create_plot(
    preview_settings,
    detector_overrides=st.session_state.detector_overrides,
    source_overrides=st.session_state.source_overrides,
)
fig_bg = "white" if theme == "Light" else "#0e1117"

try:
    show_svg(save_figure(fig, "svg", fig_bg))
except ValueError:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=fig_bg, dpi=120)
    buf.seek(0)
    st.image(buf, use_container_width=True)
plt.close(fig)

export_fig = None
download_signature = (
    settings,
    freeze_overrides(st.session_state.detector_overrides),
    freeze_overrides(st.session_state.source_overrides),
)

st.write("**Download:**")
formats = {
    "PNG": ("png", "gwsens.png", "image/png", fig_bg),
    "PDF": ("pdf", "gwsens.pdf", "application/pdf", fig_bg),
    "SVG": ("svg", "gwsens.svg", "image/svg+xml", fig_bg),
    "JPEG": ("jpeg", "gwsens.jpg", "image/jpeg", "white"),
}
c1, c2 = st.columns([1, 3])
selected_format = c1.selectbox("Format", list(formats))
fmt, filename, mime, facecolor = formats[selected_format]
if c2.button("Prepare download", use_container_width=True):
    try:
        export_fig, _ = create_plot(
            settings,
            detector_overrides=st.session_state.detector_overrides,
            source_overrides=st.session_state.source_overrides,
        )
        st.session_state.download_payload = {
            "signature": download_signature,
            "format": selected_format,
            "data": save_figure(export_fig, fmt, facecolor),
            "filename": filename,
            "mime": mime,
        }
    except ValueError:
        st.session_state.pop("download_payload", None)
        st.caption("Download temporarily unavailable - adjust a setting to refresh")
    finally:
        if export_fig:
            plt.close(export_fig)

payload = st.session_state.get("download_payload")
if (
    payload
    and payload["signature"] == download_signature
    and payload["format"] == selected_format
):
    st.download_button(
        f"Download {selected_format}",
        payload["data"],
        payload["filename"],
        payload["mime"],
    )

st.divider()
st.subheader("References")
det_refs = get_detector_references(selected_det)
src_refs = get_source_references(selected_src)
if det_refs or src_refs:
    if det_refs:
        st.write("**Sensitivity curves:**")
        for ref in det_refs:
            link = f" - [link]({ref['url']})" if ref["url"] else ""
            st.markdown(f"- **{ref['name']}**: {ref['reference']}{link}")
    if src_refs:
        st.write("**Sources:**")
        for ref in src_refs:
            link = f" - [link]({ref['url']})" if ref["url"] else ""
            st.markdown(f"- **{ref['name']}**: {ref['reference']}{link}")
else:
    st.info("Select sensitivity curves or sources to see their references.")

st.divider()
st.caption(
    "Developed by N. Borghi | Made with [Streamlit](https://streamlit.io/) | "
    "Inspired by [gwplotter.com](http://gwplotter.com/)"
)
