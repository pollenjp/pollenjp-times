# Standard Library
import argparse
import configparser
import os
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="pollenjp times arguements")
    parser.add_argument(
        "--config",
        type=lambda x: Path(x).expanduser().resolve(),
        help="config file path",
    )
    parser.add_argument(
        "--name", type=str, default="pollenjp_times_bot", help="systemd service name 'args.name'.service"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    config_filename: str = f"{args.name}.service"
    python_path: Path = Path(__file__).parent / "src" / "main.py"
    shell_file_path: Path = Path(__file__).parent / "exe" / f"{args.name}.sh"
    target_systemd_conf_path: Path = Path("~").expanduser() / ".config" / "systemd" / "user" / config_filename

    # shell script

    shell_file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(shell_file_path, "wt") as f:
        f.write("#!/bin/bash\n")
        f.write(f'{sys.executable} "{python_path.resolve()}" --config "{args.config}"')
    os.chmod(shell_file_path, 0o755)  # rwxr-xr-x

    # systemd

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
    config["Service"]["ExecStart"] = f"{shell_file_path}"
    config["Service"]["Restart"] = "always"
    config["Install"]["WantedBy"] = "default.target"

    with open(target_systemd_conf_path, "wt") as f:
        config.write(f)


if __name__ == "__main__":
    main()
