import os
import random
import shutil
import string
from pathlib import Path

import torch
import whisper
from whisper.utils import get_writer

from decipher.ff import run


def transcribe(video_in, output_dir, model, language, task, subs):
    video_in = Path(video_in).absolute()
    assert video_in.exists(), f"File {video_in} does not exist"
    output_dir = set_workdir(output_dir)
    audio_file = video_in.stem + ".aac"

    run(
        ["ffmpeg", "-y", "-i", str(video_in), "-vn", "-acodec", "copy", audio_file],
        desc=f"Convert {video_in.name} to {audio_file}",
    )

    gpu = torch.cuda.is_available()
    model = whisper.load_model(model)
    result = model.transcribe(
        audio_file, task=task, language=language, verbose=True, fp16=gpu
    )
    writer = get_writer("srt", ".")

    tmp_srt = "".join([random.choice(string.ascii_lowercase) for _ in range(15)])
    writer(result, tmp_srt)
    srt_file = video_in.stem + ".srt"
    shutil.move(tmp_srt + ".srt", srt_file)

    assert os.path.exists(srt_file), f"SRT file not generated?"
    if subs:
        subtitle(video_in, output_dir, srt_file, subs)
        return

    file_janitor()
    print(f"Output -> {output_dir}")


def subtitle(video_in, output_dir, subs, task):
    video_in, subs = Path(video_in).absolute(), Path(subs).absolute()
    assert video_in.exists(), f"File {video_in} does not exist"
    assert subs.exists(), f"File {subs} does not exist"
    output_dir = set_workdir(output_dir)

    if task == "burn":
        video_out = video_in.stem + "_output" + video_in.suffix
        ass_file = video_in.stem + ".ass"

        run(
            ["ffmpeg", "-y", "-i", str(subs), ass_file],
            desc=f"Convert {subs.name} to {ass_file}",
        )

        with open(ass_file, "r", encoding="utf-8") as file:
            data = file.readlines()
        for i in range(len(data)):
            if data[i].startswith("Style"):
                data[
                    i
                ] = "Style: Default,Open Sans,16,&H00FFFFFF,&H000000FF,&H80000000,&H80000000,-1,0,0,0,100,100,0,0,4,0,0,2,10,10,10,1\n"
                break
        with open(ass_file, "w", encoding="utf-8") as file:
            file.writelines(data)

        run(
            ["ffmpeg", "-y", "-i", str(video_in), "-vf", f"ass={ass_file}", video_out],
            desc=f"Burning {ass_file} into {video_in.name}",
        )

    else:
        video_out = video_in.stem + "_output.mkv"

        run(
            ["ffmpeg", "-y", "-i", str(video_in), "-i", str(subs), video_out],
            desc=f"Add {subs.name} to {video_in.name}",
        )

    file_janitor()
    print(f"Output -> {output_dir}")


def file_janitor():
    for file in os.listdir():
        if file.endswith(".ass") or file.endswith(".aac"):
            os.remove(file)


def set_workdir(folder):
    folder = os.path.abspath(folder)
    if not os.path.exists(folder):
        os.makedirs(folder)
    os.chdir(folder)
    assert os.getcwd() == folder
    return folder
