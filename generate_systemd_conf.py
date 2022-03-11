# Standard Library
import sys
from pathlib import Path
from typing import Any
from typing import Dict


def main():
    # variable
    config_filename: str = "pollenjp_times_bot.service"
    python_path: Path = Path(__file__).parent / "src" / "main.py"
    target_systemd_conf_path: Path = Path("~").expanduser() / ".config" / "systemd" / "user" / config_filename

    proj_root_dir: Path = Path(__file__).parent
    assert proj_root_dir.samefile(Path.cwd()), f"Run in project root directory: {proj_root_dir}"

    target_systemd_conf_path.parent.mkdir(parents=True, exist_ok=True)

    config_dict: Dict[str, Any] = {
        "Unit": {},
        "Service": {},
        "Install": {},
    }

    config_dict["Unit"]["Description"] = "pollenJP Times Job"
    config_dict["Service"]["WorkingDirectory"] = f"{proj_root_dir}"
    config_dict["Service"]["ExecStart"] = f'{sys.executable} "{python_path.resolve()}"'
    config_dict["Service"]["Restart"] = "always"
    config_dict["Install"]["WantedBy"] = "default.target"

    with open(target_systemd_conf_path, "wt") as f:
        for sec_key, sec_dict in config_dict.items():
            f.write(f"[{sec_key}]\n")
            for key, value in sec_dict.items():
                f.write(f"{key}={value}\n")


if __name__ == "__main__":
    main()
