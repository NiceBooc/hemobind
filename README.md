# HemoBind

**HemoBind** is a modular, automated pipeline for molecular docking and molecular dynamics (MD) simulations. It provides a user-friendly PySide6-based GUI to orchestrate complex scientific workflows, supporting both proprietary (Schrödinger) and open-source (OpenMM) backends.

## Features

- **Automated Docking**: Supports AutoDock-GPU and Vina.
- **Hybrid MD Backend**: Switch between Schrödinger (Desmond) and OpenMM with a single click.
- **Intelligent Preparation**: Integrated PDBFixer and OpenFF (Sage) for open-source workflows, and PrepWizard for Schrödinger.
- **Real-time Monitoring**: Integrated console and pipeline status tracking.
- **Session Management**: Save and resume complex simulation campaigns.

## Installation

### Prerequisites
- Python 3.10+
- PySide6
- OpenBabel
- AutoDock-GPU or Vina
- (Optional) Schrödinger Suite
- (Optional) OpenMM, PDBFixer, OpenFF Toolkit

### Setup
```bash
git clone https://github.com/NiceBooc/hemobind.git
cd hemobind
pip install -r requirements.txt
```

## Usage
Run the GUI application:
```bash
python3 -m hemobind_gui
```

## License
MIT License
