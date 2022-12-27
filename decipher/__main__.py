import os
import sys

import click
import whisper

from decipher.action import transcribe, subtitle
from decipher.ffexec import get_ffmpeg_exe


@click.group(name='decipher', help='transcribe videos easily using openai whisper')
def cli():
    pass


@cli.command(name='transcribe', help='transcribe a video')
@click.option('-i', '--input', required=True, prompt="Enter video file path", type=str, help='input video file path e.g. video.mp4')
@click.option('-o', '--output_dir', type=str, default='result', help='output directory path')
@click.option('--model', default='small', help='name of the whisper model to use', type=click.Choice(whisper.available_models()))
@click.option('--language', default=None, help='language spoken in the audio')
@click.option('--task', default='transcribe', help='whether to perform X->X speech recognition (\'transcribe\') or X->English translation (\'translate\')', type=click.Choice(['transcribe', 'translate']))
@click.option('-a', '--subtitle_action', default=None, help='whether to perform subtitle add or burn action', type=click.Choice(['add','burn']))
def _transcribe_cli(input, output_dir, model, language, task, subtitle_action):
    transcribe(
        input,
        output_dir,
        model,
        language,
        task,
        subtitle_action
    )


@cli.command(name='subtitle', help='subtitle a video')
@click.option('-i', '--input', required=True, prompt="Enter video file path", type=str, help='input video file path e.g. video.mp4')
@click.option('-o', '--output_dir', type=str, default='result', help='output directory path')
@click.option('-s', '--subtitle_file', prompt="Enter subtitles file path", required=True, type=str, help='input subtitles path e.g. subtitle.srt')
@click.option('-a', '--subtitle_action', default='burn', help='whether to perform subtitle add or burn action', type=click.Choice(['add','burn']))
def _subtitle_cli(input, output_dir, subtitle_file, subtitle_action):
    subtitle(
        input,
        output_dir,
        subtitle_file,
        subtitle_action
    )


def main():
    os.environ["PROJECT_PATH"] = os.path.dirname(__file__)
    os.environ["PATH"] += os.pathsep + os.path.join(os.environ["PROJECT_PATH"], "bin")
    get_ffmpeg_exe()
    cli()


if __name__ == '__main__':
    sys.exit(main())
