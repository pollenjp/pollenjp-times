# Standard Library
import argparse
import configparser
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

    python_path: Path = Path(__file__).parent / "src" / "main.py"
    target_systemd_conf_path: Path = Path("~").expanduser() / ".config" / "systemd" / "user" / f"{args.name}.service"
    systemd_env_file_path: Path = target_systemd_conf_path.parent / f"{args.name}.env"

    proj_root_dir: Path = Path(__file__).parent
    assert proj_root_dir.samefile(Path.cwd()), f"Run in project root directory: {proj_root_dir}"

    # env vars file

    systemd_env_file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(systemd_env_file_path, "wt") as f:
        f.write(f"PYTHON_FILEPATH={python_path}\n")
        f.write(f"PYTHON_ARGS=--config {args.config}\n")

    # systemd

    target_systemd_conf_path.parent.mkdir(parents=True, exist_ok=True)

    config = configparser.ConfigParser()
    config.optionxform = str

    config["Unit"] = {}
    config["Service"] = {}
    config["Install"] = {}

    config["Unit"]["Description"] = "pollenJP Times Job"
    config["Service"]["WorkingDirectory"] = f"{proj_root_dir}"
    config["Service"]["EnvironmentFile"] = f"{systemd_env_file_path}"
    config["Service"]["ExecStart"] = f"{sys.executable} $PYTHON_FILEPATH $PYTHON_ARGS"
    config["Service"]["Restart"] = "always"
    config["Install"]["WantedBy"] = "default.target"

    with open(target_systemd_conf_path, "wt") as f:
        config.write(f)


if __name__ == "__main__":
    main()
