import os
import sys

import click
import whisper

from decipher.actions import set_workdir, transcribe, subtitle
from decipher.ffexec import get_ffmpeg_exe


@click.group(name='decipher', help='transcribe videos easily using openai whisper')
def cli():
    pass


@cli.command(name='transcribe', help='transcribe a video')
@click.option('-i', '--input', required=True, prompt="Enter video file path", type=str, help='input video file path e.g. video.mp4')
@click.option('-o', '--output', type=str, default='result', help='output directory path')
@click.option('--model', default='small', help='name of the whisper model to use', type=click.Choice(whisper.available_models()))
@click.option('--language', default=None, help='language spoken in the audio')
@click.option('--task', default='transcribe', help='whether to perform X->X speech recognition (\'transcribe\') or X->English translation (\'translate\')', type=click.Choice(['transcribe', 'translate']))
@click.option('--subs', '-s', default=None, help='whether to perform subtitle add or burn action', type=click.Choice(['add','burn']))
def transcribe_cmd(input, output, model, language, task, subs):
    transcribe(
        os.path.abspath(input),
        set_workdir(output),
        model,
        language,
        task,
        subs
    )


@cli.command(name='subtitle', help='subtitle a video')
@click.option('-i', '--input', required=True, prompt="Enter video file path", type=str, help='input video file path e.g. video.mp4')
@click.option('-o', '--output', type=str, default='result', help='output directory path')
@click.option('--subs', '-s', prompt="Enter subtitles file path", required=True, type=str, help='input subtitles path e.g. subtitle.srt')
@click.option('--task', default='burn', help='whether to perform subtitle add or burn action', type=click.Choice(['add','burn']))
def subtitle_cmd(input, output, subs, task):
    subs = os.path.abspath(subs)
    subtitle(
        os.path.abspath(input),
        set_workdir(output),
        subs,
        task
    )


def main():
    os.environ["PROJECT_PATH"] = os.environ["PROJECT_PATH"] = os.path.dirname(__file__)
    os.environ["PATH"] += os.pathsep + os.path.join(os.environ["PROJECT_PATH"], "bin")
    get_ffmpeg_exe()
    cli()


if __name__ == '__main__':
    sys.exit(main())
