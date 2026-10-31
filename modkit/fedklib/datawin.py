"""GameMaker data.win handling via UndertaleModTool's CLI (bundled or downloaded)."""
import os
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

UTMT_VERSION = "0.9.2.0"
UTMT_URL = ("https://github.com/UnderminersTeam/UndertaleModTool/releases/download/"
            f"{UTMT_VERSION}/UTMT_CLI_v{UTMT_VERSION}-Windows.zip")


def tools_dir():
    return Path(__file__).resolve().parent.parent / "tools"


def utmt_exe():
    return tools_dir() / "utmt" / "UndertaleModCli.exe"


def scripts_dir():
    return tools_dir() / "utmt_scripts"


def ensure_utmt(quiet=False):
    exe = utmt_exe()
    if exe.exists():
        return exe
    if not quiet:
        print("[fedk] UndertaleModTool CLI not found - downloading %s ..." % UTMT_VERSION)
    dest = tools_dir() / "utmt"
    dest.mkdir(parents=True, exist_ok=True)
    tmp = tools_dir() / "utmt.zip"
    urllib.request.urlretrieve(UTMT_URL, tmp)
    with zipfile.ZipFile(tmp) as z:
        z.extractall(dest)
    tmp.unlink(missing_ok=True)
    if not exe.exists():
        raise RuntimeError("UndertaleModCli.exe not found after extraction")
    return exe


def run_script(datawin, script, out=None, env=None, overwrite=True):
    exe = ensure_utmt()
    cmd = [str(exe), "load", str(datawin), "-s", str(script)]
    if out:
        cmd += ["-o", str(out)]
        if overwrite:
            cmd.append("-f")
    e = dict(os.environ)
    if env:
        e.update({k: str(v) for k, v in env.items()})
    # GameMaker builds may externalize texture pages next to data.win. Run the
    # tool from that folder so UndertaleModTool can resolve those paths.
    p = subprocess.run(cmd, capture_output=True, text=True, env=e,
                       cwd=str(Path(datawin).resolve().parent))
    ok = p.returncode == 0 and "Script execution failed" not in p.stdout
    if not ok:
        raise RuntimeError("UTMT script failed:\n" + (p.stdout or "")[-4000:] + (p.stderr or "")[-2000:])
    return p.stdout
