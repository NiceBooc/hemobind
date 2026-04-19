# HemoBind

**HemoBind** is a state-of-the-art, automated pipeline designed for high-throughput molecular docking and molecular dynamics (MD) simulations. It bridges the gap between flexible open-source tools and industry-standard proprietary software, providing a unified, modular interface for drug discovery research.

## Core Concepts

HemoBind is built on the idea of **Hybrid Interoperability**. It recognizes that while open-source tools like OpenMM are powerful and freely distributable, many laboratories still rely on the Schrödinger Suite for specific validated workflows. HemoBind allows you to swap the entire simulation backend with a single click while maintaining a consistent data pipeline.

### The Pipeline Workflow

1.  **Preparation**: Automated cleaning and standardization of protein and ligand structures.
2.  **Docking**: Concurrent docking of multiple ligands using **AutoDock-GPU** (for maximum performance) or **Vina**.
3.  **Interaction Analysis**: Deep profiling of binding poses using **PLIP** (Protein-Ligand Interaction Profiler) via Docker.
4.  **Pose Selection**: Intelligent filtering of docking results based on binding affinity and interaction patterns.
5.  **MD Setup & Solvation**: Adding water boxes and ions. Supporting **PDBFixer/OpenFF** or **PrepWizard/Desmond**.
6.  **Simulation**: GPU-accelerated MD runs using **OpenMM** or **Desmond**.

## Architecture & Modularity

The project is strictly decoupled into a core computational engine and a modern graphical interface.

- **`hemobind/`**: The scientific core. Each stage is a discrete Python module.
- **`hemobind_gui/`**: A PySide6 application that provides real-time monitoring and configuration.
- **`ARCHITECTURE.md`**: Refer to this file for detailed information on the internal data flow and how to extend the pipeline.

## System Dependencies

### Required
- **Python 3.10+**
- **OpenBabel**: For chemical file format conversions.
- **Docker**: Required for the PLIP analysis stage.
- **AutoDock-GPU** / **Vina**: Must be accessible in your system `PATH`.

### MD Backend Options
You can use either of the following (or both):

#### 1. OpenMM (Open Source - Recommended)
Install via Conda:
```bash
conda install -c conda-forge openmm pdbfixer openff-toolkit openmmforcefields
```

#### 2. Schrödinger Suite (Proprietary)
Ensure the Schrödinger installation directory is accessible (e.g., `/opt/schrodinger202X`).

## Getting Started

1.  **Clone and Install Dependencies**:
    ```bash
    git clone https://github.com/NiceBooc/hemobind.git
    cd hemobind
    pip install -r requirements.txt
    ```
2.  **Launch the GUI**:
    ```bash
    python3 -m hemobind_gui
    ```
3.  **Configuration**:
    - Set your tool paths in the **Tools -> Settings** menu.
    - Check the **Pipeline Control** dock on the left to ensure all dependencies are detected.

## Developer Participation

HemoBind is designed for extension. You can easily add new docking engines (e.g., Gold, Glide) or MD backends (e.g., GROMACS) by following the patterns defined in `ARCHITECTURE.md`.

## License
MIT License
