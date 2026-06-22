# KLayout Lithography Toolbox

[Versão em Português](README_PT.md)

This repository contains the **NIST Lithography & Nanophotonics** and **NIST MEMS & NEMS** PCell libraries based on the *CNST Nanolithography Toolbox*, ported and optimized for Python using KLayout's native API (`pya`).

## Features
*   **147 verified and implemented PCells** (including Rectangular/Hexagonal/Polar Arrays, Verniers, Fractals, Grating Couplers, Waveguides, Circular Springs, Thermal Actuators, Bolometers, Anchored Flexures, etc.).
*   Fully compatible with KLayout (automatically loaded on startup).
*   Portable and easy to distribute.

## Installation

### Linux / macOS (Automated)
You can easily install the package using the included installation script:

1.  Open the terminal in the cloned project directory.
2.  Run the script:
    ```bash
    chmod +x install.sh
    ./install.sh
    ```
3.  Open or restart KLayout. The `NIST_LithoToolbox` and `NIST_MEMS_NEMS` libraries will be available for use in the PCells palette.

### Windows / Others (Manual)
1.  Open the KLayout user directory (typically `C:\Users\<YourUser>\KLayout` or `%APPDATA%\KLayout`).
2.  Create a folder named `salt` if it does not already exist.
3.  Create a folder named `klayout-lithography-toolbox` inside `salt`.
4.  Copy the `grain.xml` file, and the `pymacros` and `python` folders into it.
5.  Open or restart KLayout.

## Testing PCells locally
You can validate that all PCells compile and generate geometry without errors by running the included validation script (in batch mode):
```bash
klayout -b -r python/test_all_pcells.py
```

## Repository Structure
*   `grain.xml`: KLayout package metadata.
*   `install.sh`: Fast installation script for Unix-based systems.
*   `pymacros/`: Auto-run macro script (`register_library.lym`) that initializes the libraries upon KLayout startup.
*   `python/`: Implementation of the PCells and drawing helpers (`cnst_extended.py`, `cnst_extended_pcells.py`, `register_library.py`).
*   `python/test_all_pcells.py`: Validation script.

## Original Source & Credits
This project is a direct Python port of the geometric layouts and algorithms from the **CNST Nanolithography Toolbox**, developed and maintained by the *National Institute of Standards and Technology (NIST)*.
*   **Original Source:** [NIST CNST Nanolithography Toolbox](https://www.nist.gov/cnst/co-shared-nanofabrication-project/cnst-nanolithography-toolbox)
*   **Documentation & Reference Code:** The behavior and parameters of the PCells were based on the original Java implementation of the toolbox.

## AI Model Used
All code porting, refactoring, geometry bug fixing, duplicate cleaning, automated testing, and repository structuring were created and executed by:
*   **AI Agent:** Antigravity (an autonomous software engineering AI agent designed by the Google DeepMind team).
*   **Underlying LLM:** Gemini 1.5 Pro (Google DeepMind).
