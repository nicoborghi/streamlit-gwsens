# GWSens

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://app-gwsens.streamlit.app/)

Interactive gravitational wave sensitivity curve plotter.

![GWSens Screenshot](data/gwsens.png)

## Features

- Plot detector sensitivity curves and GW sources
- Light/Dark themes
- Customizable labels, colors, and positions
- Export to PNG, PDF, SVG, JPEG
- LaTeX rendering support

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Notebook Usage

Use the same plotting code outside Streamlit:

```python
from gwsens import PlotSettings, create_plot

settings = PlotSettings(
    detectors=("LISA", "aLIGOD", "ET"),
    sources=("GW150914", "GW230814"),
    figsize=(9, 5),
)
fig, ax = create_plot(settings)
fig
```

## Data

Add custom detectors/sources by placing CSV files in `data/detectors/` or `data/sources/` and updating `config.py`.

`GW230814` is included as the current GWTC-4.0 loudest LVK compact-binary
coalescence by matched-filter SNR. GWOSC lists `GW230814_230901` with SNR 43.0,
source chirp mass 26.78 `M_sun`, and luminosity distance 290 Mpc. The plotted
curve converts the existing `GW150914` characteristic-strain curve with the
standard inspiral scaling `h_c proportional to M_chirp^(5/6) / D_L`, plus a
small detector-frame total-mass frequency rescale.

## References

Inspired by [gwplotter.com](http://gwplotter.com/)
