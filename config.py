"""
Configuration for GWSens - Gravitational Wave Sensitivity Curves

This file contains all detector and source configurations.
To add a new detector or source, simply add a new entry to the respective dictionary.

For detectors with variants (e.g., ET triangle vs ET 2L):
  - Use 'variants' list with alternative names
  - First variant is shown by default if no specific variant selected
  - Set 'variant_of' to link to parent detector (shares same data file)
"""

# =============================================================================
# PATHS
# =============================================================================
DATA_DIR_DETECTORS = "data/detectors/"
DATA_DIR_SOURCES = "data/sources/"

# =============================================================================
# PLOT DEFAULTS
# =============================================================================
PLOT_DEFAULTS = {
    "figsize": (9, 5),
    "dpi": 300,
    "label_fontsize": 8,
    "label_fontweight": "bold",
    "grid_linestyle": "dotted",
    "grid_linewidth": 0.8,
    "grid_alpha": 0.8,
    "gradient_alpha": 0.8,
}

AXIS_DEFAULTS = {
    "x_min": 0.4e-10,
    "x_max": 1.4e+6,
    "y_min": 1e-26,
    "y_max": 1.1e-12,
}

THEME_SETTINGS = {
    "Light": {
        "detector_color": "#000000",
        "label_linewidth": 2,
        "label_color": "#ffffff",
        "style": "default",
    },
    "Dark": {
        "detector_color": "#ffffff",
        "label_linewidth": 0,
        "label_color": "#ffffff",
        "style": "dark_background",
    },
}

# =============================================================================
# DETECTOR CONFIGURATIONS (Sensitivity Curves)
# =============================================================================
# Each detector entry contains:
#   - label: Display name (plain text)
#   - label_latex: LaTeX version of label (optional, for plot rendering)
#   - file: JSON filename (without path)
#   - default_selected: Whether selected by default
#   - label_x, label_y: Label position on plot
#   - category: Detector category (for grouping)
#   - reference: Citation/reference info
#   - reference_url: URL to paper/documentation (optional)
#   - variants: List of alternative names (optional)
#               First variant shown by default, others available in dropdown
#   - variant_of: Parent detector key if this is a variant (optional)
#   - params: Optional detector-specific parameters
#
# To add a new detector:
#   1. Add the JSON data file to data/detectors/
#   2. Add a new entry below with unique key
#
# To add a variant of existing detector:
#   1. Add new entry with 'variant_of' pointing to parent
#   2. Can use same or different data file
# =============================================================================

DETECTORS = {
    # -------------------------------------------------------------------------
    # Pulsar Timing Arrays
    # -------------------------------------------------------------------------
    "EPTA": {
        "label": "EPTA",
        "file": "EPTA.csv",
        "default_selected": False,
        "label_x": 2e-6,
        "label_y": 5e-13,
        "category": "Pulsar Timing",
        "reference": "Desvignes et al. (2016), MNRAS 458, 3341",
        "reference_url": "https://doi.org/10.1093/mnras/stw483",
        "params": {"N_pulsars": 5, "ObsTime": 10, "ObsRate": 14, "TimingPrec": 1e-7},
    },
    "IPTA": {
        "label": "IPTA",
        "file": "IPTA.csv",
        "default_selected": True,
        "label_x": 2e-6,
        "label_y": 1e-13,
        "category": "Pulsar Timing",
        "reference": "Verbiest et al. (2016), MNRAS 458, 1267",
        "reference_url": "https://doi.org/10.1093/mnras/stw347",
        "params": {"N_pulsars": 20, "ObsTime": 15, "ObsRate": 14, "TimingPrec": 1e-7},
    },
    "SKA": {
        "label": "SKA",
        "file": "SKA.csv",
        "default_selected": False,
        "label_x": 2e-6,
        "label_y": 7.5e-15,
        "category": "Pulsar Timing",
        "reference": "Janssen et al. (2015), PoS AASKA14, 037",
        "reference_url": "https://doi.org/10.22323/1.215.0037",
        "params": {"N_pulsars": 100, "ObsTime": 20, "ObsRate": 14, "TimingPrec": 3e-8},
    },
    # -------------------------------------------------------------------------
    # Space-based Detectors
    # -------------------------------------------------------------------------
    "eLISA": {
        "label": "eLISA",
        "file": "eLISA.csv",
        "default_selected": False,
        "label_x": 1.5e-6,
        "label_y": 7e-17,
        "category": "Space-based",
        "reference": "Amaro-Seoane et al. (2012), Class. Quantum Grav. 29, 124016",
        "reference_url": "https://doi.org/10.1088/0264-9381/29/12/124016",
    },
    "LISA": {
        "label": "LISA",
        "file": "LISA.csv",
        "default_selected": True,
        "label_x": 2e-6,
        "label_y": 1e-18,
        "category": "Space-based",
        "reference": "LISA Collaboration (2017), arXiv:1702.00786",
        "reference_url": "https://arxiv.org/abs/1702.00786",
    },
    "DECIGO": {
        "label": "DECIGO",
        "file": "DECIGO.csv",
        "default_selected": False,
        "label_x": 7e-2,
        "label_y": 1e-23,
        "category": "Space-based",
        "reference": "Kawamura et al. (2011), Class. Quantum Grav. 28, 094011",
        "reference_url": "https://doi.org/10.1088/0264-9381/28/9/094011",
    },
    "BBO": {
        "label": "BBO",
        "file": "BBO.csv",
        "default_selected": False,
        "label_x": 4.2e-3,
        "label_y": 2e-24,
        "category": "Space-based",
        "reference": "Crowder & Cornish (2005), Phys. Rev. D 72, 083005",
        "reference_url": "https://doi.org/10.1103/PhysRevD.72.083005",
    },
    "ALIA": {
        "label": "ALIA",
        "file": "ALIA.csv",
        "default_selected": False,
        "label_x": 1e-1,
        "label_y": 7e-22,
        "category": "Space-based",
        "reference": "Baker et al. (2019), arXiv:1907.11305",
        "reference_url": "https://arxiv.org/abs/1907.11305",
    },
    "TianQin": {
        "label": "TianQin",
        "file": "TianQin.csv",
        "default_selected": False,
        "label_x": 2.5e+0,
        "label_y": 1.5e-18,
        "category": "Space-based",
        "reference": "Luo et al. (2016), Class. Quantum Grav. 33, 035010",
        "reference_url": "https://doi.org/10.1088/0264-9381/33/3/035010",
    },
    "LGWA": {
        "label": "LGWA",
        "file": "LGWA.csv",
        "default_selected": True,
        "label_x": 2e-3,
        "label_y": 1.2e-17,
        "category": "Lunar",
        "reference": "Harms et al. (2021), ApJ 910, 1",
        "reference_url": "https://doi.org/10.3847/1538-4357/abe5a7",
    },
    # -------------------------------------------------------------------------
    # Ground-based Detectors
    # -------------------------------------------------------------------------
    "GEO": {
        "label": "GEO",
        "file": "GEO.csv",
        "default_selected": False,
        "label_x": 2e+4,
        "label_y": 1.55e-18,
        "category": "Ground-based",
        "reference": "Luck et al. (2010), J. Phys.: Conf. Ser. 228, 012012",
        "reference_url": "https://doi.org/10.1088/1742-6596/228/1/012012",
    },
    "LIGO": {
        "label": "LIGO",
        "file": "LIGO.csv",
        "default_selected": False,
        "label_x": 2e+4,
        "label_y": 7.99e-19,
        "category": "Ground-based",
        "reference": "Abbott et al. (2009), Rep. Prog. Phys. 72, 076901",
        "reference_url": "https://doi.org/10.1088/0034-4885/72/7/076901",
    },
    "aLIGO-O1": {
        "label": "aLIGO-O1",
        "file": "aLIGO-O1.csv",
        "default_selected": False,
        "label_x": 2e+4,
        "label_y": 1.5e-20,
        "category": "Ground-based",
        "reference": "LIGO Scientific Collaboration (2015), Class. Quantum Grav. 32, 074001",
        "reference_url": "https://doi.org/10.1088/0264-9381/32/7/074001",
    },
    "aLIGOD": {
        "label": "aLIGOD",
        "file": "aLIGOD.csv",
        "default_selected": True,
        "label_x": 2e+4,
        "label_y": 4e-21,
        "category": "Ground-based",
        "reference": "LIGO Scientific Collaboration (2015), Class. Quantum Grav. 32, 074001",
        "reference_url": "https://doi.org/10.1088/0264-9381/32/7/074001",
    },
    "ApLIGO": {
        "label": "ApLIGO",
        "label_latex": r"LIGO A$^+$",
        "file": "ApLIGO.csv",
        "default_selected": False,
        "label_x": 2e+4,
        "label_y": 1.51e-21,
        "category": "Ground-based",
        "reference": "LIGO A+ Design",
        "reference_url": "https://dcc.ligo.org/LIGO-T1800042/public",
    },
    "Virgo": {
        "label": "Virgo",
        "file": "Virgo.csv",
        "default_selected": False,
        "label_x": 2e+4,
        "label_y": 4.12e-19,
        "category": "Ground-based",
        "reference": "Acernese et al. (2015), Class. Quantum Grav. 32, 024001",
        "reference_url": "https://doi.org/10.1088/0264-9381/32/2/024001",
    },
    "aVirgo": {
        "label": "aVirgo",
        "file": "aVirgo.csv",
        "default_selected": False,
        "label_x": 2e+4,
        "label_y": 2.13e-19,
        "category": "Ground-based",
        "reference": "Acernese et al. (2015), Class. Quantum Grav. 32, 024001",
        "reference_url": "https://doi.org/10.1088/0264-9381/32/2/024001",
    },
    "KAGRA": {
        "label": "KAGRA",
        "file": "KAGRA.csv",
        "default_selected": False,
        "label_x": 2e+4,
        "label_y": 2.92e-20,
        "category": "Ground-based",
        "reference": "Aso et al. (2013), Phys. Rev. D 88, 043007",
        "reference_url": "https://doi.org/10.1103/PhysRevD.88.043007",
    },
    # ET with variants - first one (triangle) is default
    "ET": {
        "label": "ET",
        "label_latex": "ET",
        "file": "ET.csv",
        "default_selected": True,
        "label_x": 2e+4,
        "label_y": 3e-22,
        "category": "Ground-based",
        "reference": "Punturo et al. (2010), Class. Quantum Grav. 27, 194002",
        "reference_url": "https://doi.org/10.1088/0264-9381/27/19/194002",
        "variants": ["ET triangle", "ET 2L"],  # Alternative display names
    },
    "CE": {
        "label": "CE",
        "file": "CE.csv",
        "default_selected": False,
        "label_x": 2e+4,
        "label_y": 1e-22,
        "category": "Ground-based",
        "reference": "Abbott et al. (2017), Class. Quantum Grav. 34, 044001",
        "reference_url": "https://doi.org/10.1088/1361-6382/aa51f4",
    },
}

# =============================================================================
# SOURCE CONFIGURATIONS
# =============================================================================
# Each source entry contains:
#   - label: Display name (can include \n for multiline)
#   - label_latex: LaTeX version of label (optional)
#   - file: JSON filename (without path)
#   - default_selected: Whether selected by default
#   - color: Display color (hex)
#   - label_x, label_y: Label position on plot
#   - reference: Citation/reference info
#   - reference_url: URL to paper/documentation (optional)
#   - params: Optional source-specific parameters
#
# To add a new source:
#   1. Add the JSON data file to data/sources/
#   2. Add a new entry below with unique key
# =============================================================================

SOURCES = {
    "BKG": {
        "label": "Stochastic\nbackground",
        "label_latex": r"Stochastic" + "\n" + r"background",
        "file": "BKG.csv",
        "default_selected": True,
        "color": "#b81414",
        "label_x": 7.6e-11,
        "label_y": 3.7e-14,
        "reference": "Cosmological background",
        "reference_url": None,
    },
    "SMBBH": {
        "label": "Supermassive\nbinaries",
        "label_latex": r"Supermassive" + "\n" + r"binaries",
        "file": "SMBBH.csv",
        "default_selected": True,
        "color": "#e2922f",
        "label_x": 3.5e-7,
        "label_y": 1e-17,
        "reference": "Sesana et al. (2008), MNRAS 390, 192",
        "reference_url": "https://doi.org/10.1111/j.1365-2966.2008.13682.x",
    },
    "GalBinRes": {
        "label": "Resolvable\ngalactic binaries",
        "file": "GalBinRes.csv",
        "default_selected": True,
        "color": "#287a28",
        "label_x": 5e-7,
        "label_y": 9e-22,
        "reference": "Nelemans et al. (2001), A&A 375, 890",
        "reference_url": "https://doi.org/10.1051/0004-6361:20010683",
    },
    "GalBinUnres": {
        "label": "Unresolvable\ngalactic binaries",
        "file": "GalBinUnres.csv",
        "default_selected": True,
        "color": "#d8b200",
        "label_x": 5e-7,
        "label_y": 8e-23,
        "reference": "Nelemans et al. (2001), A&A 375, 890",
        "reference_url": "https://doi.org/10.1051/0004-6361:20010683",
    },
    "MBBH": {
        "label": "Massive\nbinaries",
        "label_latex": r"Massive" + "\n" + r"binaries ($M \sim 10^6 M_\odot$)",
        "file": "MBBH.csv",
        "default_selected": True,
        "color": "#29cc29",
        "label_x": 5e-5,
        "label_y": 4e-18,
        "reference": "SMBH mergers",
        "reference_url": None,
    },
    "EMRI": {
        "label": "Extreme mass\nratio inspirals",
        "file": "EMRI.csv",
        "default_selected": True,
        "color": "#a5d800",
        "label_x": 5e-7,
        "label_y": 1e-20,
        "reference": "Babak et al. (2017), Phys. Rev. D 95, 103012",
        "reference_url": "https://doi.org/10.1103/PhysRevD.95.103012",
    },
    "SNIa": {
        "label": "SNIa",
        "file": "SNIa.csv",
        "default_selected": False,
        "color": "#209469",
        "label_x": 3.3e-1,
        "label_y": 2e-20,
        "reference": "Falta et al. (2011), Phys. Rev. Lett. 106, 201103",
        "reference_url": "https://doi.org/10.1103/PhysRevLett.106.201103",
    },
    "CBC": {
        "label": "CBC",
        "file": "CBC.csv",
        "default_selected": True,
        "color": "#2396a6",
        "label_x": 3e+3,
        "label_y": 3e-23,
        "reference": "NS-NS, NS-BH, BH-BH mergers",
        "reference_url": None,
    },
    "CCSN": {
        "label": "CCSN",
        "file": "CCSN.csv",
        "default_selected": True,
        "color": "#6f117b",
        "label_x": 3e+3,
        "label_y": 4e-24,
        "reference": "Ott (2009), Class. Quantum Grav. 26, 063001",
        "reference_url": "https://doi.org/10.1088/0264-9381/26/6/063001",
        "params": {"Dist": 0.3},
    },
    "PSR": {
        "label": "Pulsars",
        "label_latex": r"Pulsars ($h \propto \epsilon I f^2 / d$)",
        "file": "PSR.csv",
        "default_selected": False,
        "color": "#30123b",
        "label_x": 8e+4,
        "label_y": 5e-25,
        "reference": "Continuous GW from rotating NS",
        "reference_url": None,
        "params": {"AmplScale": 1},
    },
    "GW150914": {
        "label": "GW150914",
        "file": "GW150914.csv",
        "default_selected": True,
        "color": "#1d72b7",
        "label_x": 3e+1,
        "label_y": 7e-21,
        "reference": "Abbott et al. (2016), Phys. Rev. Lett. 116, 061102",
        "reference_url": "https://doi.org/10.1103/PhysRevLett.116.061102",
    },
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_default_detectors():
    return [k for k, v in DETECTORS.items() if v.get("default_selected")]

def get_default_sources():
    return [k for k, v in SOURCES.items() if v.get("default_selected")]

def get_detector_references(keys):
    refs, seen = [], set()
    for k in keys:
        if k in DETECTORS and (ref := DETECTORS[k].get("reference")) and ref not in seen:
            seen.add(ref)
            refs.append({"name": DETECTORS[k]["label"], "reference": ref, "url": DETECTORS[k].get("reference_url")})
    return refs

def get_source_references(keys):
    refs, seen = [], set()
    for k in keys:
        if k in SOURCES and (ref := SOURCES[k].get("reference")) and ref not in seen:
            seen.add(ref)
            refs.append({"name": SOURCES[k]["label"].replace("\n", " "), "reference": ref, "url": SOURCES[k].get("reference_url")})
    return refs


