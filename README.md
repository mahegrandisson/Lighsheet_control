# Lighsheet_control

**Lighsheet_control** is a control interface for light sheet microscopes. It allows users to control galvos, PI stages, and execute scan sequences via a graphical interface built with PyQt5 and Napari.

---

## Features

- **Galvo Control** – Adjust the X and Y galvo positions.
- **PI Stage Control** – Move Z, Theta, X, and Y stages using PI controllers.
- **Automated Scanning** – Define and execute custom scan routines.
- **User Interface** – Intuitive GUI built on Napari and PyQt5.

---

## Requirements

- Python 3.8+
- [PyQt5](https://pypi.org/project/PyQt5/)
- [Napari](https://napari.org/)
- [pymmcore-plus](https://pypi.org/project/pymmcore-plus/)
- [pipython](https://pypi.org/project/pipython/)
- [pyyaml](https://pypi.org/project/PyYAML/)

You can install all required packages using the command below.

---

## Installation

Clone this repository and install dependencies:

```bash
  git clone https://github.com/mahegrandisson/Lighsheet_control.git
  cd Lighsheet_control
  pip install -r requirements.txt
```


## Configuration
Initial parameters for the galvos and PI stages are defined in:

```arduino
config/galvo_pi_config.yaml
```


## Usage

to start the app, run:
```bash
  python main.py
```

A graphical interface will launch, allowing you to:

- Control stage movement

- Adjust galvo positions

- Execute and configure scans




