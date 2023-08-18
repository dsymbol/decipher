import argparse
import os
import sys

from whisper import available_models

from decipher.action import subtitle, transcribe
from decipher.ffdl import get_ffmpeg_exe

os.environ["PATH"] += os.pathsep + os.path.join(os.path.dirname(__file__), "bin")


@click.group(name='decipher', help='transcribe videos easily using openai whisper')
@click.version_option(version='1.0.0-partial', prog_name='decipher')  # replace '1.0.0' with your desired version number

def cli():
    pass


@cli.command(name='transcribe', help='transcribe a video')
@click.option('-i', '--input', required=True, prompt="Enter video file path", type=str, help='input video file path e.g. video.mp4')
@click.option('-o', '--output_dir', type=str, default='result', help='output directory path')
@click.option('--model', default='small', help='name of the whisper model to use', type=click.Choice(whisper.available_models()))
@click.option('--language', default=None, help='language spoken in the audio')
@click.option('--task', default='transcribe', help='whether to perform X->X speech recognition (\'transcribe\') or X->English translation (\'translate\')', type=click.Choice(['transcribe', 'translate']))
@click.option('-a', '--subtitle_action', default=None, help='whether to perform subtitle add or burn action', type=click.Choice(['add', 'burn']))
@click.option('--minute', type=int, default=None, help='specific minute of the video to transcribe')
def _transcribe_cli(input, output_dir, model, language, task, subtitle_action, minute):
    transcribe(
        input,
        output_dir,
        model,
        language,
        task,
        subtitle_action,
        minute
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
        default="small",
        type=str,
        choices=available_models(),
        help="name of the whisper model to use",
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
            args.subtitle_action,
        )
    elif args.action == "subtitle":
        subtitle(args.input, args.output_dir, args.subtitle_file, args.subtitle_action)


if __name__ == "__main__":
    sys.exit(main())
