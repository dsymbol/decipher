import argparse
import os
from pathlib import Path

import whisper

from decipher import transcribe, subtitle
from ._ffmpeg import get_ffmpeg_exe
from .decipher import set_workdir


def cli():
    parser = argparse.ArgumentParser(
        prog="decipher", description="Transcribe videos easily using OpenAI's whisper"
    )
    action = parser.add_subparsers(
        dest="action", required=True
    )
    transcribe = action.add_parser(
        "transcribe",
        help="transcribe a video file",
    )
    transcribe.add_argument("-i",
                            "--input",
                            metavar="",
                            type=str, required=True, help="input video file path e.g. video.mp4")
    transcribe.add_argument(
        "-o",
        "--output",
        type=str,
        default="result",
        metavar="",
        help="output directory path",
    )
    transcribe.add_argument(
        "--model",
        type=str,
        default="small",
        choices=whisper.available_models(),
        help="name of the whisper model to use",
    )
    transcribe.add_argument(
        "--task",
        type=str,
        default="transcribe",
        choices=["transcribe", "translate"],
        help="whether to perform X->X speech recognition ('transcribe') or X->English translation ('translate')",
    )
    transcribe.add_argument(
        "--subs", "-s",
        type=str,
        default=None,
        choices=["add", "burn"],
        help="whether to perform subtitle add or burn action",
    )

    subtitle = action.add_parser(
        "subtitle",
        help="subtitle a video file using an available srt file",
    )
    subtitle.add_argument("-i",
                          "--input",
                          metavar="",
                          type=str, required=True, help="input video file path e.g. video.mp4")
    subtitle.add_argument(
        "-o",
        "--output",
        type=str,
        default="result",
        metavar="",
        help="output directory path",
    )
    subtitle.add_argument("--subs", "-s", metavar="", required=True, type=str,
                          help="input subtitles path e.g. subtitle.srt")
    subtitle.add_argument(
        "--task",
        type=str,
        default="burn",
        choices=["add", "burn"],
        help="whether to perform subtitle add or burn action",
    )
    return parser.parse_args()


def main():
    os.environ["PROJECT_PATH"] = os.environ["PROJECT_PATH"] = str(Path(__file__).parent)
    os.environ["PATH"] += os.pathsep + os.path.join(os.environ["PROJECT_PATH"], "bin")
    get_ffmpeg_exe()

    args = cli()
    if args.action == "transcribe":
        transcribe(
            os.path.abspath(args.input),
            set_workdir(args.output),
            args.model,
            args.task,
            args.subs
        )
    elif args.action == "subtitle":
        subs = os.path.abspath(args.subs)
        subtitle(
            os.path.abspath(args.input),
            set_workdir(args.output),
            subs,
            args.task
        )
