"""
s7_md.py — Desmond Molecular Dynamics (multisim).
"""
import concurrent.futures
from pathlib import Path
from hemobind.config import HemobindConfig
from hemobind.utils.schrodinger import run_multisim
from hemobind.utils.logger import get_logger

log = get_logger("hemobind.s7")


def run(config: HemobindConfig, run_dir: Path, context: dict) -> dict:
    md_setup_dir: Path = context.get("md_setup_dir", run_dir / "md_setup")
    built_cms_files: list[Path] = context.get("built_cms_files", [])
    if not built_cms_files:
        raise ValueError("No built CMS files found in context")

    md_results = []

    def _run_single(input_cms: Path):
        jobname = f"{input_cms.stem.replace('_build-out', '')}_md"
        msj_file = md_setup_dir / f"{jobname}.msj"
        _write_md_msj(msj_file, sim_time=config.md.sim_time_ns)

        out_cms = md_setup_dir / f"{jobname}-out.cms"
        
        run_multisim(
            schrodinger=config.md.schrodinger,
            jobname=jobname,
            msj_file=msj_file,
            input_cms=input_cms,
            output_cms=out_cms
        )
        return out_cms

    log.info(f"Running Desmond MD on {len(built_cms_files)} candidates...")

    # MD usually runs on GPU, running many in parallel might crash.
    # We follow config.md.cpu_jobs but note that Desmond might use GPUs independently.
    for cms in built_cms_files:
        try:
            res = _run_single(cms)
            md_results.append(res)
        except Exception as e:
            log.error(f"MD failed for {cms.name}: {e}")
            raise

    log.info("Molecular Dynamics completed for all selected poses.")
    return {**context, "md_results": md_results}


def _write_md_msj(msj_file: Path, sim_time: float):
    msj_content = f"""task {{
  task = "desmond:auto"
}}

simulate {{
  time = {sim_time}
  ensemble = {{
    class = NPT
    method = MTK
    thermostat = {{
      tau = 1.0
    }}
    barostat = {{
      tau = 2.0
    }}
  }}
  temperature = 300.0
  pressure = 1.01325
}}
"""
    msj_file.write_text(msj_content)
