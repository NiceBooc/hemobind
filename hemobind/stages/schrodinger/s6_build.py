"""
s6_build.py — Desmond System Builder (multisim).
"""
import concurrent.futures
import tarfile
import shutil
from pathlib import Path
from hemobind.config import HemobindConfig
from hemobind.utils.schrodinger import run_multisim
from hemobind.utils.logger import get_logger

log = get_logger("hemobind.s6")


def run(config: HemobindConfig, run_dir: Path, context: dict) -> dict:
    md_setup_dir: Path = context.get("md_setup_dir", run_dir / "md_setup")
    prepped_maes: list[Path] = context.get("prepped_maes", [])
    if not prepped_maes:
        raise ValueError("No prepped MAE files found in context")

    built_cms_files = []

    def _run_single(input_mae: Path):
        jobname = f"{input_mae.stem}_build"
        msj_file = md_setup_dir / f"{jobname}.msj"
        _write_build_msj(
            msj_file,
            buffer_size=config.md.box_buffer_ang,
            solvent=config.md.water_model,
            salt_conc=config.md.salt_conc_mol
        )

        out_cms = md_setup_dir / f"{jobname}-out.cms"
        
        run_multisim(
            schrodinger=config.md.schrodinger,
            jobname=jobname,
            msj_file=msj_file,
            input_cms=input_mae,
            output_cms=out_cms
        )
        
        # multisim puts the actual CMS inside a TGZ. Stage number varies.
        all_tgz = sorted(md_setup_dir.glob(f"{jobname}_*-out.tgz"))
        if all_tgz:
            tgz_file = all_tgz[-1] # Take the last stage
            log.info(f"Extracting {tgz_file.name}...")
            with tarfile.open(tgz_file, "r:gz") as tar:
                # Extract only the .cms file
                for member in tar.getmembers():
                    if member.name.endswith("-out.cms"):
                        tar.extract(member, path=md_setup_dir)
                        # The extracted file is in a subfolder {jobname}_3/
                        extracted_cms = md_setup_dir / member.name
                        shutil.move(str(extracted_cms), str(out_cms))
                        # Clean up subfolder
                        shutil.rmtree(md_setup_dir / member.name.split("/")[0], ignore_errors=True)
                        break

        if not out_cms.exists():
            raise RuntimeError(f"System Builder failed to produce {out_cms.name}")

        return out_cms

    log.info(f"Running System Builder on {len(prepped_maes)} candidates "
             f"({config.md.cpu_jobs} parallel workers)...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=config.md.cpu_jobs) as executor:
        futures = {executor.submit(_run_single, mae): mae for mae in prepped_maes}
        for future in concurrent.futures.as_completed(futures):
            mae = futures[future]
            try:
                cms = future.result()
                built_cms_files.append(cms)
            except Exception as e:
                log.error(f"System Builder failed for {mae.name}: {e}")
                raise

    log.info("System Building completed for all selected poses.")
    return {**context, "built_cms_files": built_cms_files}


def _write_build_msj(msj_file: Path, buffer_size: float, solvent: str, salt_conc: float):
    msj_content = f"""task {{
  task = "desmond:auto"
}}

build_geometry {{
  add_counterion = {{
    ion = Na
    number = neutralize_system
  }}
  box = {{
    shape = orthorhombic
    size = [{buffer_size} {buffer_size} {buffer_size}]
    size_type = buffer
  }}
  rezero_system = false
  salt = {{
    concentration = {salt_conc}
    negative_ion = Cl
    positive_ion = Na
  }}
  solvent = {solvent}
}}

assign_forcefield {{
}}
"""
    msj_file.write_text(msj_content)
