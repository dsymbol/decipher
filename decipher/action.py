import os
import shutil
from pathlib import Path
from tempfile import mktemp

import torch
from transformers import pipeline
from dataclasses import dataclass

from decipher.ff import run

root = Path(__file__).parent


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

    with open(temp_srt, "w", encoding="utf-8") as f:
        for index, chunk in enumerate(outputs['chunks']):
            start_time = seconds_to_srt_time_format(chunk['timestamp'][0])
            end_time = seconds_to_srt_time_format(chunk['timestamp'][1])
            f.write(f"{index + 1}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{chunk['text'].strip()}\n\n")


@dataclass
class ResultFiles:
    output_dir: str
    subtitle_file: str
    video_file: str


def transcribe(video_in, output_dir=None, model="medium", language=None, task="transcribe", batch_size=24,
               subtitle_action=None) -> ResultFiles:
    video_in = Path(video_in).absolute()
    assert video_in.exists(), f"File {video_in} does not exist"

    if output_dir:
        output_dir = Path(output_dir).absolute()
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = Path(os.getcwd())

    audio_file = mktemp(suffix=".aac", dir=output_dir)

    run(
        ["ffmpeg", "-y", "-i", str(video_in), "-vn", "-acodec", "copy", audio_file],
        desc=f"Convert {video_in.suffix.upper()} to {Path(audio_file).suffix.upper()}",
    )

    temp_srt = mktemp(suffix=".srt", dir=output_dir)
    audio_to_srt(audio_file, temp_srt, model, task, language, batch_size)
    os.remove(audio_file)
    srt_filename = output_dir / f"{video_in.stem}.srt"
    shutil.move(temp_srt, srt_filename)

    assert os.path.exists(srt_filename), f"SRT file not generated?"

    result = None
    if subtitle_action:
        result = subtitle(video_in, srt_filename, output_dir, subtitle_action)

    return ResultFiles(
        str(output_dir),
        str(srt_filename),
        str(result.video_file) if result else None
    )


def subtitle(video_in, subtitle_file, output_dir=None, action="burn") -> ResultFiles:
    video_in = Path(video_in).absolute()
    subtitle_file = Path(subtitle_file).absolute()
    assert video_in.exists(), f"File {video_in} does not exist"
    assert subtitle_file.exists(), f"File {subtitle_file} does not exist"

    if output_dir:
        output_dir = Path(output_dir).absolute()
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = Path(os.getcwd())

    if action == "burn":
        video_out = output_dir / f"{video_in.stem}_out{video_in.suffix}"
        run(
            ["ffmpeg", "-y", "-i", str(video_in), "-vf",
             f"subtitles={str(subtitle_file.name)}:force_style='Fontname=Arial,Fontsize=16,OutlineColour=&H80000000,BorderStyle=4,"
             "BackColour=&H80000000,Outline=0,Shadow=0,MarginV=10,Alignment=2,Bold=-1'",
             str(video_out)],
            cwd=str(subtitle_file.parent),  # https://trac.ffmpeg.org/ticket/3334
            desc=f"Burning {subtitle_file.suffix.upper()} into {video_in.suffix.upper()}",
        )
    else:
        video_out = output_dir / f"{video_in.stem}_out.mkv"
        run(
            ["ffmpeg", "-y", "-i", str(video_in), "-i", str(subtitle_file), str(video_out)],
            desc=f"Add {subtitle_file.suffix.upper()} to .MKV",
        )

    return ResultFiles(
        str(output_dir),
        str(subtitle_file),
        str(video_out)
    )
