import os
import shutil
from pathlib import Path
from tempfile import mktemp

import torch
from transformers import pipeline

from decipher.ff import run


def seconds_to_srt_time_format(seconds):
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)
    return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"


def audio_to_srt(audio_file, temp_srt, model="medium", task="transcribe", language=None, batch_size=24):
    if torch.cuda.is_available():
        device = "cuda"
        dtype = torch.float16
    elif torch.backends.mps.is_available():
        device = "mps"
        dtype = torch.float16
    else:
        device = "cpu"
        dtype = torch.float32

    print(f"{device.upper()} is being used for this transcription, this process may take a while.")

    pipe = pipeline(
        "automatic-speech-recognition",
        model=f"openai/whisper-{model}",
        torch_dtype=dtype,
        device=device,
        model_kwargs={"attn_implementation": "sdpa"},
    )

    if device == "mps":
        torch.mps.empty_cache()

    outputs = pipe(
        audio_file,
        chunk_length_s=30,
        batch_size=batch_size,
        generate_kwargs={"task": task, "language": language},
        return_timestamps=True,
    )

    with open(temp_srt, "w") as f:
        for index, chunk in enumerate(outputs['chunks']):
            start_time = seconds_to_srt_time_format(chunk['timestamp'][0])
            end_time = seconds_to_srt_time_format(chunk['timestamp'][1])
            f.write(f"{index + 1}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{chunk['text'].strip()}\n\n")


def transcribe(video_in, output_dir, model, language, task, batch_size, subs):
    video_in = Path(video_in).absolute()
    assert video_in.exists(), f"File {video_in} does not exist"
    output_dir = set_workdir(output_dir)
    audio_file = mktemp(suffix=".aac", dir=os.getcwd())

    run(
        ["ffmpeg", "-y", "-i", str(video_in), "-vn", "-acodec", "copy", audio_file],
        desc=f"Convert {video_in.suffix.upper()} to {Path(audio_file).suffix.upper()}",
    )

    temp_srt = mktemp(suffix=".srt", dir=os.getcwd())
    audio_to_srt(audio_file, temp_srt, model, task, language, batch_size)
    os.remove(audio_file)
    srt_filename = video_in.stem + ".srt"
    shutil.move(temp_srt, srt_filename)

    assert os.path.exists(srt_filename), f"SRT file not generated?"
    if subs:
        subtitle(video_in, output_dir, srt_filename, subs)
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
