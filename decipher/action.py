import os
from pathlib import Path

import ffmpeg
import torch
import whisper
from whisper.utils import get_writer

from ffpb import main as ffpb


def transcribe(video_in, output_dir, model, language, task, subs, minute=None):
    video_in = Path(video_in).absolute()
    output_dir = set_workdir(output_dir)
    audio_file = video_in.stem + ".aac"

    # Define the start and end times for the specific minute if provided
    stream = ffmpeg.input(video_in)
    
    if minute is not None:
        start_time = f"{minute}:00"
        duration = "60"  # 60 seconds
        stream = stream.output(audio_file, ss=start_time, t=duration, vn=None, acodec='copy')
    else:
        stream = stream.output(audio_file, vn=None, acodec='copy')
        
    stream = stream.overwrite_output()
    execute(stream, desc=f"Converting {video_in.name} to {audio_file}...")

    gpu = torch.cuda.is_available()
    model = whisper.load_model(model)
    result = model.transcribe(audio_file, task=task, language=language, verbose=True, fp16=gpu)
    writer = get_writer("srt", ".")

    writer(result, video_in.stem)
    srt_file = video_in.stem + ".srt"

    assert os.path.exists(srt_file), f"SRT file not generated?"
    if subs:
        subtitle(video_in, output_dir, srt_file, subs)
        return

    file_janitor()
    print(f"Output -> {output_dir}")



def subtitle(video_in, output_dir, subs, task):
    video_in, subs = Path(video_in).absolute(), Path(subs).absolute()
    output_dir = set_workdir(output_dir)
    if task == "burn":
        video_out = video_in.stem + "_output" + video_in.suffix
        ass_file = video_in.stem + ".ass"

        stream = (
            ffmpeg
            .input(subs)
            .output(ass_file, f='ass')
            .overwrite_output()
        )
        execute(stream, desc="Converting `SubRip Subtitle file` to `Advanced SubStation Alpha file`")

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

        stream = (
            ffmpeg
            .input(video_in)
            .output(video_out, vf=f'ass={ass_file}')
            .overwrite_output()
        )
        execute(stream, desc=f"Burning `Advanced SubStation Alpha file` into {video_in.name}...")

    else:
        video_out = video_in.stem + "_output.mkv"

        input_ffmpeg = ffmpeg.input(video_in)
        input_ffmpeg_sub = ffmpeg.input(subs)

        input_video = input_ffmpeg['v']
        input_audio = input_ffmpeg['a']
        input_subtitles = input_ffmpeg_sub['s']
        stream = ffmpeg.output(
            input_video, input_audio, input_subtitles, video_out,
            vcodec='copy', acodec='copy', scodec='srt'
        )
        stream = ffmpeg.overwrite_output(stream)
        execute(stream, desc=f"Adding `SubRip Subtitle file` to {video_in.name}")

    file_janitor()
    print(f"Output -> {output_dir}")


def execute(stream, desc=None):
    if desc: print(desc)
    args = ffmpeg.get_args(stream)
    ffpb(args)


def file_janitor():
    for file in os.listdir():
        if file.endswith('.ass') or file.endswith('.aac'):
            os.remove(file)


def set_workdir(folder):
    folder = os.path.abspath(folder)
    if not os.path.exists(folder):
        os.mkdir(folder)
    os.chdir(folder)
    assert os.getcwd() == folder
    return folder
