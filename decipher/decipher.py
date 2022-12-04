import os
import shlex
import subprocess
import sys
from pathlib import Path
from time import sleep
from typing import Optional, Literal

import whisper

from ._transcribe import cli


def transcribe(input: str,
               output: Optional[str] = "result",
               model: Optional[str] = "small",
               language: Optional[str] = None,
               task: Optional[str] = "transcribe",
               subs: Literal["add", "burn"] = None):
    audio = change_file_extension(input, "aac")
    run(
        f"ffmpeg -y -i '{input}' -vn -acodec copy '{audio}'",
        desc="Extracting audio file...",
    )

    args = ["--model", model, "--task", task, audio]
    if language: args.extend(["--language", language])
    whisper.transcribe.cli = cli
    whisper.transcribe.cli(args)
    srt = change_file_extension(input, "srt")
    assert os.path.exists(srt), f"SRT file not generated?"
    if subs:
        subtitle(input, output, srt, subs)
        return
    print(f"result >> {output}")


def subtitle(input, output, subs, task: Literal["add", "burn"]):
    if task == "burn":
        out = change_file_suffix(input, "_out")
        ass = change_file_extension(input, "ass")
        run(
            f"ffmpeg -y -i '{subs}' '{ass}'",
            desc="Converting .SRT to .ASS",
        )
        with open(ass, "r", encoding="utf-8") as file:
            data = file.readlines()
        for i in range(len(data)):
            if data[i].startswith("Style"):
                data[
                    i
                ] = "Style: Default,Verdana,14,&H00FFFFFF,&H000000FF,&H80000000,&H80000000,-1,0,0,0,100,100,0,0,4,0,0,2,10,10,10,1\n"
                break
        with open(ass, "w", encoding="utf-8") as file:
            file.writelines(data)
        run(
            f"ffmpeg -y -i '{input}' -vf 'ass={ass}' '{out}'",
            desc="Burning subtitles...",
        )
    else:
        out = change_file_extension(input, "mkv")
        run(
            f"ffmpeg -y -i '{input}' -i '{subs}' -scodec copy '{out}'",
            desc="Adding subtitles...",
        )
    print(f"result >> {output}")


def change_file_extension(file, extension):
    filename = Path(file).stem + "." + extension
    return filename


def change_file_suffix(file, suffix):
    video = os.path.basename(file)
    filename = video.split(".")
    filename[-2] = filename[-2] + suffix
    filename = ".".join(filename)
    return filename


def run(command, desc=None):
    if desc:
        print(desc)
        sleep(2)
    command = shlex.split(command, posix=False if sys.platform == "win32" else True)
    p = subprocess.run(command, text=True)

    if p.returncode != 0:
        message = (
            f"Error running command.\n"
            f"Command: {p.args}\n"
            f"Error code: {p.returncode}\n"
        )
        raise RuntimeError(message)

    return p.returncode


def set_workdir(folder):
    folder = os.path.abspath(folder)
    if not os.path.exists(folder):
        os.mkdir(folder)
    os.chdir(folder)
    assert os.getcwd() == folder
    return folder
