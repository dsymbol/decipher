import argparse
import errno
import os
import shutil
import subprocess
import time
from pathlib import Path

import whisper

import _transcribe
from _ffmpeg import get_ffmpeg_exe


def onerror(function, path, exc_info):
    if (
        function is os.rmdir
        and issubclass(exc_info[0], OSError)
        and exc_info[1].errno == errno.ENOTEMPTY
    ):
        timeout = 0.001
        while timeout < 2:
            if not os.listdir(path):
                return os.rmdir(path)
            time.sleep(timeout)
            timeout *= 2
    raise


def clean_dir(path):
    shutil.rmtree(path, onerror=onerror)
    timeout = 0.001
    while True:
        try:
            return os.mkdir(path)
        except PermissionError as e:
            if e.winerror != 5 or timeout >= 2:
                raise
            time.sleep(timeout)
            timeout *= 2


def run(command, desc=None, errdesc=None):
    if desc is not None:
        print(desc)

    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )

    for line in result.stdout:
        print(line)

    if result.returncode != 0:
        message = f"""{errdesc or 'Error running command'}.
        Command: {command}
        Error code: {result.returncode}
        stdout: {result.stdout.decode(encoding="utf8", errors="ignore") if len(result.stdout) > 0 else '<empty>'}
        stderr: {result.stderr.decode(encoding="utf8", errors="ignore") if len(result.stderr) > 0 else '<empty>'}
        """
        raise RuntimeError(message)

    return result.stdout.decode(encoding="utf8", errors="ignore")


class SubtitleVideo:
    def __init__(self, model, video_file, task):
        self.model = model
        self.video_file = os.path.abspath(video_file)
        self.task = task
        self.tmp_dir = os.path.join(os.environ["PROJECT_PATH"], "tmp")
        self.audio_file = os.path.join(self.tmp_dir, "audio.aac")
        self.srt_file = os.path.join(self.tmp_dir, "subtitles.srt")
        self.ass_file = os.path.join(self.tmp_dir, "subtitles.ass")

    def extract_audio_file(self):
        result = run(
            f"ffmpeg -i {self.video_file} -vn -acodec copy {self.audio_file}",
            desc="Extracting audio file...",
        )
        return result

    def transcribe(self):
        whisper.transcribe.cli = _transcribe.cli
        args = ["--model", self.model, "--output_dir", self.tmp_dir, self.audio_file]
        if self.task.lower() == "translate":
            args.extend(["--task", "translate"])
        whisper.transcribe.cli(args)

    def srt_to_ass(self):
        self.ass_file = os.path.join(os.environ["PROJECT_PATH"], "tmp", "subtitles.ass")
        result = run(
            f"ffmpeg -i {self.srt_file} {self.ass_file}", desc="Converting .SRT to .ASS"
        )
        with open(self.ass_file, "r", encoding="utf-8") as file:
            data = file.readlines()
        for i in range(len(data)):
            if data[i].startswith("Style"):
                data[
                    i
                ] = "Style: Default,Verdana,14,&H00FFFFFF,&H000000FF,&H80000000,&H80000000,-1,0,0,0,100,100,0,0,4,0,0,2,10,10,10,1\n"
                break
        with open(self.ass_file, "w", encoding="utf-8") as file:
            file.writelines(data)
        return result

    def burn_subtitles_into_video(self):
        out_file = self.video_file.split(".")
        out_file[-2] = out_file[-2] + "_out"
        out_file = ".".join(out_file)
        out_file = os.path.join(os.environ["PROJECT_PATH"], out_file)
        os.chdir(self.tmp_dir)
        run(
            f"ffmpeg -y -i {self.video_file} -vf ass=subtitles.ass {out_file}",
            desc="Burning subtitles...",
        )
        return os.path.abspath(out_file)

    def run(self):
        clean_dir(self.tmp_dir) if os.path.exists(self.tmp_dir) else os.mkdir(
            self.tmp_dir
        )
        self.extract_audio_file()
        self.transcribe()
        self.srt_to_ass()
        print("output file >> " + self.burn_subtitles_into_video())


def cli():
    parser = argparse.ArgumentParser(
        prog="decipher", description="Transcribe videos easily using openai's whisper"
    )
    parser.add_argument("video", type=str, help="input video path e.g. video.mp4")
    parser.add_argument(
        "--model",
        default="small",
        choices=whisper.available_models(),
        help="name of the whisper model to use",
    )
    parser.add_argument(
        "--task",
        type=str,
        default="transcribe",
        choices=["transcribe", "translate"],
        help="whether to perform X->X speech recognition ('transcribe') or X->English translation ('translate')",
    )
    args = parser.parse_args()
    SubtitleVideo(args.model, args.video, args.task).run()


if __name__ == "__main__":
    os.environ["PROJECT_PATH"] = os.environ["PROJECT_PATH"] = str(Path(__file__).parent)
    ffmpeg = get_ffmpeg_exe()
    os.environ['PATH'] += os.pathsep + str(Path(ffmpeg).parent)
    cli()
