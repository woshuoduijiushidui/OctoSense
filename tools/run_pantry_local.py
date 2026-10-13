"""Launch the fork desktop with App Hub and AI services for Pantry Steward."""
import argparse
import importlib.util
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "pantry-steward"


def main():
    parser = argparse.ArgumentParser(description="最新版冰箱管家本地运行")
    parser.add_argument("--hidden", action="store_true")
    parser.add_argument("--remote", type=int)
    parser.add_argument("--app-data", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("pantry_launch", APP / "tools" / "launch.py")
    launch = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(launch)
    launch.ROOT = ROOT
    launch.BUILD = ROOT / "target" / "pantry-official-tools"
    os.environ["CARGO_NET_GIT_FETCH_WITH_CLI"] = "true"
    hub, _, installer = launch.prepare_tools(args.offline, check_only=args.check)
    launch.run([hub, "check", APP / "bundle", "--allow-unsigned"])
    if args.check:
        return
    command = ["cargo", "build", "--release", "--locked", "--no-default-features",
               "--features", "app-hub,octos-core", "-p", "octosense"]
    if args.offline:
        command.append("--offline")
    launch.run(command, cwd=ROOT)
    if args.build:
        return
    profile = (args.app_data or APP / ".local-state").resolve()
    mirror, data, anchor = launch.local_install(hub, installer, False, profile)
    env = dict(os.environ, OCTOSENSE_HUB=str(mirror), OCTOSENSE_HUB_CATALOG="legacy",
               OCTOSENSE_HUB_ANCHOR=anchor, OCTOSENSE_APP_DATA=str(data),
               OCTOSENSE_HOME=str(profile / "desktop-home"), RINX_DATA_DIR=str(profile / "rinx"))
    if args.hidden:
        env["MAKEPAD_HIDE_WINDOWS"] = "1"
    else:
        env.pop("MAKEPAD_HIDE_WINDOWS", None)
    if args.remote:
        env["MAKEPAD_REMOTE"] = str(args.remote)
    else:
        env.pop("MAKEPAD_REMOTE", None)
    launch.run([ROOT / "target" / "release" / "octosense.exe",
                "--test-action", "launch-hub:pantry-steward"], cwd=ROOT, env=env)


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print("启动失败：" + str(error), file=sys.stderr)
        sys.exit(1)
