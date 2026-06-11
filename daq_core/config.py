from pathlib import Path
import yaml


def load_config(path: str = "config.yaml") -> dict:
    config_path = Path(path)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with config_path.open("r") as file:
        return yaml.safe_load(file)