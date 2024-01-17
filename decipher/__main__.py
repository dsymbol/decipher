import argparse
import os
import sys

from decipher.action import subtitle, transcribe
from decipher.ff import get_ffmpeg_exe

os.environ["PATH"] += os.pathsep + os.path.join(os.path.dirname(__file__), "bin")


def cli():
    parser = argparse.ArgumentParser(
        prog="decipher", description="Transcribe videos easily using openai whisper"
    )
    subparsers = parser.add_subparsers(required=True, dest="action")

    t = subparsers.add_parser("transcribe", help="transcribe a video")
    t.add_argument(
        "-i",
        "--input",
        required=True,
        type=str,
        help="input video file path e.g. video.mp4",
    )
    t.add_argument(
        "-o", "--output_dir", type=str, default="result", help="output directory path"
    )
    t.add_argument(
        "--model",
        default="medium",
        type=str,
        help="name of the whisper model to use https://huggingface.co/openai/whisper-large-v3#model-details",
    )
    t.add_argument(
        "--language", type=str, default=None, help="language spoken in the audio"
    )
    t.add_argument(
        "--task",
        type=str,
        default="transcribe",
        choices=["transcribe", "translate"],
        help="whether to perform X->X speech recognition ('transcribe') or X->English translation ('translate')",
    )
    t.add_argument(
        "--batch_size",
        required=False,
        type=int,
        default=24,
        help="number of parallel batches you want to compute. reduce if you face OOMs.",
    )
    t.add_argument(
        "-a",
        "--subtitle_action",
        type=str,
        default=None,
        choices=["add", "burn"],
        help="whether to perform subtitle add or burn action",
    )

    s = subparsers.add_parser("subtitle", help="subtitle a video")
    s.add_argument(
        "-i",
        "--input",
        required=True,
        type=str,
        help="input video file path e.g. video.mp4",
    )
    s.add_argument(
        "-o", "--output_dir", type=str, default="result", help="output directory path"
    )
    s.add_argument(
        "-s",
        "--subtitle_file",
        required=True,
        type=str,
        help="input subtitles path e.g. subtitle.srt",
    )
    s.add_argument(
        "-a",
        "--subtitle_action",
        type=str,
        default="burn",
        choices=["add", "burn"],
        help="whether to perform subtitle add or burn action",
    )
    return parser.parse_args()


def main():
    get_ffmpeg_exe()
    args = cli()

    if args.action == "transcribe":
        transcribe(
            args.input,
            args.output_dir,
            args.model,
            args.language,
            args.task,
            args.batch_size,
            args.subtitle_action,
        )
    elif args.action == "subtitle":
        subtitle(args.input, args.output_dir, args.subtitle_file, args.subtitle_action)


if __name__ == "__main__":
    sys.exit(main())
