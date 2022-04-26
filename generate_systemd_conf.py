# Standard Library
import configparser
import sys
from pathlib import Path


def main():
    # variable
    config_filename: str = "pollenjp_times_bot.service"
    python_path: Path = Path(__file__).parent / "src" / "main.py"
    target_systemd_conf_path: Path = Path("~").expanduser() / ".config" / "systemd" / "user" / config_filename

    proj_root_dir: Path = Path(__file__).parent
    assert proj_root_dir.samefile(Path.cwd()), f"Run in project root directory: {proj_root_dir}"

    target_systemd_conf_path.parent.mkdir(parents=True, exist_ok=True)

    config = configparser.ConfigParser()
    config.optionxform = str

    config["Unit"] = {}
    config["Service"] = {}
    config["Install"] = {}

    config["Unit"]["Description"] = "pollenJP Times Job"
    config["Service"]["WorkingDirectory"] = f"{proj_root_dir}"
    config["Service"]["ExecStart"] = f'{sys.executable} "{python_path.resolve()}"'
    config["Service"]["Restart"] = "always"
    config["Install"]["WantedBy"] = "default.target"

    with open(target_systemd_conf_path, "wt") as f:
        config.write(f)


if __name__ == "__main__":
    main()
