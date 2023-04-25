import os
import platform
import shutil
import stat
import sys
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse

import requests
from tqdm import tqdm

BIN_PATH = os.path.join(os.path.dirname(__file__), 'bin')

BINARIES = {
    "Linux": {"ffmpeg": "ffmpeg-linux64-v4.1", "ffprobe": "ffprobe-linux64-v4.1"},
    "Darwin": {"ffmpeg": "ffmpeg-osx64-v4.1", "ffprobe": "ffprobe-osx64-v4.1"},
    "Windows": {"ffmpeg": "ffmpeg-win64-v4.1.exe", "ffprobe": "ffprobe-win64-v4.1.exe"}
}


def get_ffmpeg_exe(ffmpeg: bool = True, ffprobe: bool = False):
    localvars = locals().copy()
    exes = [exe for exe in ['ffmpeg', 'ffprobe'] if localvars[exe]]
    os_ = platform.system()

    for exe in exes:
        if shutil.which(exe):
            continue
        if not os.path.exists(BIN_PATH):
            os.makedirs(BIN_PATH)
        url = "https://github.com/imageio/imageio-binaries/raw/master/ffmpeg/" + BINARIES[os_][exe]
        filename = os.path.join(
            BIN_PATH, f"{exe}.exe" if os_ == "Windows" else exe
        )
        print(
            f"{exe} was not found! downloading from imageio/imageio-binaries repository."
        )
        try:
            download_file(url, filename)
        except Exception as f:
            shutil.rmtree(BIN_PATH)
            sys.exit(str(f))
        st = os.stat(filename)
        os.chmod(filename, st.st_mode | stat.S_IEXEC)


def download_file(url, filename=None):
    if not filename:
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)

    r = requests.get(url, stream=True)
    file_size = int(r.headers.get('content-length', 0))
    chunk_size = 1024

    with NamedTemporaryFile(mode='wb', delete=False) as temp, tqdm(
            desc=os.path.basename(filename),
            total=file_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
            leave=True
    ) as bar:
        for chunk in r.iter_content(chunk_size=chunk_size):
            size = temp.write(chunk)
            bar.update(size)

    os.rename(temp.name, filename)
