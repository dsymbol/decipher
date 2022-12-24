import os
from pathlib import Path
from typing import Optional, Literal

import ffmpeg
import whisper

from decipher import ffpb
from decipher.transcribe import cli


def transcribe(input: str,
               output: Optional[str] = "result",
               model: Optional[str] = "small",
               language: Optional[str] = None,
               task: Optional[str] = "transcribe",
               subs: Literal["add", "burn"] = None):
    input_base = os.path.basename(input)
    audio = change_file_extension(input, "aac")
    stream = (
        ffmpeg
        .input(input)
        .output(audio, vn=None, acodec='copy')
        .overwrite_output()
    )
    execute(stream, desc=f"Converting {input_base} to {audio}...")

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
    input_base = os.path.basename(input)
    if task == "burn":
        out = output_filename(input_base)
        ass = change_file_extension(input, "ass")

        stream = (
            ffmpeg
            .input(subs)
            .output(ass, f='ass')
            .overwrite_output()
        )
        execute(stream, desc="Converting `SubRip Subtitle file` to `Advanced SubStation Alpha file`")

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

        stream = (
            ffmpeg
            .input(input)
            .output(out, vf=f'ass={ass}')
            .overwrite_output()
        )
        execute(stream, desc=f"Burning `Advanced SubStation Alpha file` into {input_base}...")

    else:
        out = change_file_extension(input, "mkv")

        input_ffmpeg = ffmpeg.input(input)
        input_ffmpeg_sub = ffmpeg.input(subs)

        input_video = input_ffmpeg['v']
        input_audio = input_ffmpeg['a']
        input_subtitles = input_ffmpeg_sub['s']
        stream = ffmpeg.output(
            input_video, input_audio, input_subtitles, out,
            vcodec='copy', acodec='copy', scodec='srt'
        )

        stream = ffmpeg.overwrite_output(stream)
        execute(stream, desc=f"Adding `SubRip Subtitle file` to {input_base}")

    print(f"result >> {output}")


def change_file_extension(file, extension):
    filename = Path(file).stem + "." + extension
    return filename


def output_filename(filename):
    last_dot_index = filename.rfind(".")
    name = filename[:last_dot_index]
    extension = filename[last_dot_index:]
    new_name = name + "_output"
    new_filename = new_name + extension
    return new_filename


def execute(stream, desc=None):
    if desc: print(desc)
    args = ffmpeg.get_args(stream)
    ffpb.main(args)


def set_workdir(folder):
    folder = os.path.abspath(folder)
    if not os.path.exists(folder):
        os.mkdir(folder)
    os.chdir(folder)
    assert os.getcwd() == folder
    return folder
