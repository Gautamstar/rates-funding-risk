from pydantic import BaseModel
from pathlib import Path

class ProjectConfig(BaseModel):
    data_dir: Path = Path("data")
    curated_dir: Path = data_dir / "curated"
    raw_dir: Path = data_dir / "raw"
    out_dir: Path = Path("out")
    templates_dir: Path = Path("templates")
    weights: dict = {"ZFL_TO": 0.4, "GOVT": 0.4, "SHY": 0.2}

cfg = ProjectConfig()
