# HemoBind Architecture & Developer Guide

HemoBind is designed as a modular, extensible pipeline for molecular modeling. This document explains the internal structure and design philosophy to help developers modify or extend the software.

## Core Philosophy

HemoBind follows a **Separation of Concerns** principle:
1.  **Core Stages (`hemobind/stages/`)**: Pure Python logic that performs scientific calculations. These are decoupled from the UI and can be run independently.
2.  **GUI Layer (`hemobind_gui/`)**: A PySide6 wrapper that manages user interaction, configuration, and visualization.
3.  **Config System (`hemobind/config.py`)**: A centralized, type-safe configuration schema using Python dataclasses and YAML.

## Module Structure

### 1. The Pipeline Orchestrator (`hemobind/pipeline.py`)
The `Pipeline` class is the heart of the execution logic. It:
- Maintains a list of ordered stages (`STAGES`).
- Manages a **Context Object** (`context.json`) which is passed between stages. Each stage receives the output of the previous one.
- Implements **Checkpointing**: Every successfully finished stage creates a `.done` file. This allows the user to resume a failed run from a specific point.

### 2. Hybrid Backend System
HemoBind supports two major MD engines. The logic is branched in `pipeline.py` and implemented in subdirectories:
- `hemobind/stages/schrodinger/`: Uses proprietary Schrödinger Suite utilities (`prepwizard`, `multisim`).
- `hemobind/stages/openmm/`: Uses open-source tools (`PDBFixer`, `OpenFF`, `OpenMM`).

### 3. Stage Implementation Pattern
Every stage in `hemobind/stages/` must implement a `run` function:
```python
def run(config: HemobindConfig, run_dir: Path, context: dict) -> dict:
    # 1. Perform calculations
    # 2. Update context
    return context
```

## Data Flow (Context)

The `context` dictionary is the "memory" of the pipeline. Key keys include:
- `receptor_clean_pdb`: Path to the processed protein.
- `lig_pdbqts`: Dictionary mapping ligand names to their PDBQT files.
- `selected_paths`: List of PDB files chosen for MD after docking.
- `md_results`: Paths to final trajectories and logs.

## GUI Interaction (`hemobind_gui/`)

- **Worker Thread**: `PipelineWorker` runs the `Pipeline.run()` method in a separate thread to keep the UI responsive.
- **Dynamic Config Panels**: Each stage has a corresponding panel in `widgets/panels/`. These panels translate UI state into a Python dictionary that matches the `HemobindConfig` structure.
- **Dependency Checker**: `core/dependency_checker.py` uses a mix of binary existence checks (`shutil.which`) and Python module imports to verify the environment.

## Extension Guide

### How to add a new Stage
1.  Create `hemobind/stages/sX_new_stage.py`.
2.  Define the `run` function.
3.  Add the stage name to `STAGES` in `hemobind/pipeline.py`.
4.  Update `Pipeline._get_stage_fn` to include the new import.
5.  (Optional) Create a UI panel in `hemobind_gui/widgets/panels/pX_new_stage.py` and register it in `MainWindow`.

### How to add a new Backend
If you want to support GROMACS or AMBER:
1.  Create a folder `hemobind/stages/gromacs/`.
2.  Implement `s5`, `s6`, `s7` using GROMACS commands.
3.  Add a radio button to `PrepPanel` in the GUI.
4.  Update the logic in `Pipeline._get_stage_fn` to branch into your new folder.
