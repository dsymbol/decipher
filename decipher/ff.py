import os
import platform
import re
import shutil
import stat
import subprocess as sp
import sys
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse

import requests
from tqdm import tqdm

from pathlib import Path

BIN_PATH = Path(__file__).parent / "bin"
BIN_PATH.mkdir(parents=True, exist_ok=True)
os.environ["PATH"] += os.pathsep + str(BIN_PATH)

BINARIES = {
    "Linux": {"ffmpeg": "ffmpeg-linux64-v4.1", "ffprobe": "ffprobe-linux64-v4.1"},
    "Darwin": {"ffmpeg": "ffmpeg-osx64-v4.1", "ffprobe": "ffprobe-osx64-v4.1"},
    "Windows": {"ffmpeg": "ffmpeg-win64-v4.1.exe", "ffprobe": "ffprobe-win64-v4.1.exe"},
}


def get_ffmpeg_exe(ffmpeg: bool = True, ffprobe: bool = False):
    localvars = locals().copy()
    exes = [exe for exe in ["ffmpeg", "ffprobe"] if localvars[exe]]
    os_ = platform.system()

    for exe in exes:
        if shutil.which(exe):
            continue
        url = (
            "https://github.com/imageio/imageio-binaries/raw/master/ffmpeg/"
            + BINARIES[os_][exe]
        )
        filename = BIN_PATH / f"{exe}.exe" if os_ == "Windows" else exe
        print(
            f"{exe} was not found! downloading from imageio/imageio-binaries repository."
        )
        try:
            download_file(url, str(filename))
        except Exception as f:
            shutil.rmtree(str(BIN_PATH))
            sys.exit(str(f))
        st = os.stat(filename)
        os.chmod(filename, st.st_mode | stat.S_IEXEC)


def run(command: list, desc=None, cwd=None):
    """
    Adapted from Martin Larralde's code https://github.com/althonos/ffpb
    Personalized for my (dsymbol) use.
    """
    command = ["ffmpeg"] + command if command[0] != "ffmpeg" else command

    duration_exp = re.compile(r"Duration: (\d{2}):(\d{2}):(\d{2})\.\d{2}")
    progress_exp = re.compile(r"time=(\d{2}):(\d{2}):(\d{2})\.\d{2}")
    output = []

    with sp.Popen(
        command, stdout=sp.PIPE, stderr=sp.STDOUT, universal_newlines=True, text=True, cwd=cwd
    ) as p:
        with tqdm(total=None, desc=desc, unit="s", ncols=80, leave=True) as t:
            for line in p.stdout:
                output.append(line)
                if duration_exp.search(line):
                    duration = duration_exp.search(line).groups()
                    t.total = (
                        int(duration[0]) * 3600
                        + int(duration[1]) * 60
                        + int(duration[2])
                    )
                elif progress_exp.search(line):
                    progress = progress_exp.search(line).groups()
                    t.update(
                        int(progress[0]) * 3600
                        + int(progress[1]) * 60
                        + int(progress[2])
                        - t.n
                    )

    if p.returncode != 0:
        message = "\n".join(
            [
                f"Error running command.",
                f"Command: {p.args}",
                f"Return code: {p.returncode}",
                f'Output: {"".join(output)}',
            ]
        )
        raise RuntimeError(message)


def download_file(url, filename=None):
    if not filename:
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)

    r = requests.get(url, stream=True)
    file_size = int(r.headers.get("content-length", 0))
    chunk_size = 1024

    with NamedTemporaryFile(mode="wb", delete=False) as temp, tqdm(
        desc=os.path.basename(filename),
        total=file_size,
        ncols=80,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
        leave=True,
    ) as bar:
        for chunk in r.iter_content(chunk_size=chunk_size):
            size = temp.write(chunk)
            bar.update(size)

    os.rename(temp.name, filename)
