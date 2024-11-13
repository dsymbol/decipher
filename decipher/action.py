from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

import stable_whisper
import torch
from ffutils import ffprog

root = Path(__file__).parent


@dataclass
class PathStore:
    output_dir: Path
    subtitle_file: Path
    video_file: Path = None


def audio_to_srt(
    audio_file,
    model="medium",
    task="transcribe",
    language=None,
    batch_size=24,
):
    if torch.cuda.is_available():
        device = "cuda"
    elif torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"
    print(f"{device.upper()} is being used for this transcription.")

    model = stable_whisper.load_hf_whisper(model, device=device)
    result = model.transcribe(
        audio_file, language=language, task=task, batch_size=batch_size
    )
    return result.to_srt_vtt(word_level=False)


def transcribe(
    video_in,
    output_dir=".",
    model="medium",
    language=None,
    task="transcribe",
    batch_size=24,
    subtitle_action=None,
) -> PathStore:
    video_in = Path(video_in).absolute()
    assert video_in.exists(), f"File {video_in} does not exist"

    output_dir = Path(output_dir).absolute()
    output_dir.mkdir(parents=True, exist_ok=True)

    with TemporaryDirectory() as _tempdir:
        tempdir = Path(_tempdir)
        audio_file = str(tempdir / "audio.aac")

        ffprog(
            ["ffmpeg", "-y", "-i", str(video_in), "-vn", "-c:a", "aac", audio_file],
            desc=f"Extracting audio from video",
        )

        srt_text = audio_to_srt(audio_file, model, task, language, batch_size)

    srt_file = output_dir / f"{video_in.stem}.srt"
    with open(srt_file, "w", encoding="utf-8") as f:
        f.write(srt_text)

    assert srt_file.exists(), f"SRT file not generated?"

    if subtitle_action:
        store = subtitle(video_in, srt_file, output_dir, subtitle_action)
    else:
        store = PathStore(output_dir, srt_file)

    return store


def subtitle(video_in, subtitle_file, output_dir=".", action="burn") -> PathStore:
    video_in = Path(video_in).absolute()
    subtitle_file = Path(subtitle_file).absolute()
    assert video_in.exists(), f"File {video_in} does not exist"
    assert subtitle_file.exists(), f"File {subtitle_file} does not exist"

    output_dir = Path(output_dir).absolute()
    output_dir.mkdir(parents=True, exist_ok=True)

    if action == "burn":
        video_out = output_dir / f"{video_in.stem}_out.mp4"
        ffprog(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(video_in),
                "-vf",
                f"subtitles={str(subtitle_file.name)}:force_style='Fontname=Arial,Fontsize=16,OutlineColour=&H80000000,BorderStyle=4,"
                "BackColour=&H80000000,Outline=0,Shadow=0,MarginV=10,Alignment=2,Bold=-1'",
                str(video_out),
            ],
            cwd=str(subtitle_file.parent),  # https://trac.ffmpeg.org/ticket/3334
            desc=f"Burning subtitles into video",
        )
    else:
        video_out = output_dir / f"{video_in.stem}_out.mp4"
        ffprog(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(video_in),
                "-i",
                str(subtitle_file),
                "-c:s",
                "mov_text",
                str(video_out),
            ],
            desc=f"Adding subtitles to video",
        )

    return PathStore(output_dir, subtitle_file, video_out)
