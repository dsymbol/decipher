import os
import platform
import shutil
import sys
import stat


def get_ffmpeg_exe():
    if shutil.which("ffmpeg"):
        return
    url = "https://github.com/imageio/imageio-binaries/raw/master/ffmpeg/"
    _os = platform.system()
    bin_path = os.path.join(os.environ["PROJECT_PATH"], "bin")
    if not os.path.exists(bin_path): os.mkdir(bin_path)
    file = platform_specific_binary(_os, "ffmpeg")
    filename = os.path.join(
        bin_path, "ffmpeg.exe" if _os == "Windows" else "ffmpeg"
    )
    print(
        "ffmpeg was not found! downloading from imageio/imageio-binaries repository."
    )
    download_file(url + file, filename)
    st = os.stat(filename)
    os.chmod(filename, st.st_mode | stat.S_IEXEC)
    return filename


def platform_specific_binary(_os, binary):
    files = {
        "Linux": {"ffmpeg": "ffmpeg-linux64-v4.1", "ffprobe": "ffprobe-linux64-v4.1"},
        "Darwin": {"ffmpeg": "ffmpeg-osx64-v4.1", "ffprobe": "ffprobe-osx64-v4.1"},
        "Windows": {
            "ffmpeg": "ffmpeg-win64-v4.1.exe",
            "ffprobe": "ffprobe-win64-v4.1.exe",
        },
    }
    return files[_os][binary]


def download_file(url: str, filename: str, show_progress_bar=True):
    try:
        import requests
    except ImportError:
        raise ImportError(
            "requests module not found! run `pip install requests` in cmd"
        )

    if not filename:
        filename = url.split("/")[-1]
    with open(f"{filename}", "wb") as f:
        response = requests.get(url, stream=True)
        total_length = response.headers.get("content-length")
        chunk_size = 4096

        if total_length is None:
            f.write(response.content)
        else:
            dl = 0
            full_length = int(total_length)

            for data in response.iter_content(chunk_size=chunk_size):
                dl += len(data)
                f.write(data)

                if show_progress_bar:
                    complete = int(25 * dl / full_length)
                    fill_c = "#" * complete
                    unfill_c = "-" * (25 - complete)
                    sys.stdout.write(
                        f"\r{filename} {fill_c}{unfill_c} {round(dl / 1000000, 1)} / {round(full_length / 1000000, 1)} MB"
                    )
                    sys.stdout.flush()
    print()
