"""
s5_prepwiz.py — Protein Preparation Wizard via Schrödinger.
"""
import concurrent.futures
from pathlib import Path
from hemobind.config import HemobindConfig
from hemobind.utils.schrodinger import run_prepwizard
from hemobind.utils.logger import get_logger

log = get_logger("hemobind.s5")


def run(config: HemobindConfig, run_dir: Path, context: dict) -> dict:
    md_setup_dir = run_dir / "md_setup"
    md_setup_dir.mkdir(exist_ok=True)

    selected_paths: list[Path] = context.get("selected_paths", [])
    receptor_pdb: Path = context.get("receptor_clean_pdb")
    if not selected_paths:
        raise ValueError("No selected poses found in context")
    if not receptor_pdb:
        raise ValueError("Receptor PDB not found in context")

    prepped_maes = []

    def _run_single(input_pdb: Path):
        # Merge receptor and ligand pose into a complex
        complex_pdb = md_setup_dir / f"{input_pdb.stem}_complex.pdb"
        _merge_pdb(receptor_pdb, input_pdb, complex_pdb)
        
        out_mae = md_setup_dir / f"{input_pdb.stem}_prepped.mae"
        
        run_prepwizard(
            schrodinger=config.md.schrodinger,
            input_file=complex_pdb,
            output_file=out_mae,
            ph=config.md.ph,
            fillsidechains=True
        )
        return out_mae

    log.info(f"Running PrepWizard on {len(selected_paths)} candidates "
             f"({config.md.cpu_jobs} parallel workers)...")

    # Run in parallel using ThreadPoolExecutor (since it's mostly waiting for subprocess)
    with concurrent.futures.ThreadPoolExecutor(max_workers=config.md.cpu_jobs) as executor:
        futures = {executor.submit(_run_single, path): path for path in selected_paths}
        for future in concurrent.futures.as_completed(futures):
            path = futures[future]
            try:
                mae = future.result()
                prepped_maes.append(mae)
            except Exception as e:
                log.error(f"PrepWizard failed for {path.name}: {e}")
                raise

    log.info("PrepWizard completed for all selected poses.")
    return {**context, "prepped_maes": prepped_maes, "md_setup_dir": md_setup_dir}


def _merge_pdb(receptor_pdb: Path, ligand_pdb: Path, out_pdb: Path) -> None:
    rec_lines = [l for l in receptor_pdb.read_text().splitlines() if not l.startswith("END")]
    lig_lines = [l for l in ligand_pdb.read_text().splitlines() if l.startswith(("ATOM", "HETATM"))]
    out_pdb.write_text("\n".join(rec_lines + lig_lines + ["END\n"]))
