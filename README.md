<div align="center">
<h1>Decipher 📺️</h1>
<img src="https://user-images.githubusercontent.com/88138099/195132806-0ac06b96-8989-47d0-ba99-39cb808938d2.png"/>
</div>

Effortlessly add [openai/whisper](https://github.com/openai/whisper) AI generated transcription subtitles into provided
video.  
You can choose whether to perform X->X speech recognition or X->English translation.

**What is whisper?**  
Whisper is an automatic State-of-the-Art speech recognition system from OpenAI that has been trained on 680,000 hours
of multilingual and multitask supervised data collected from the web. This large and diverse dataset leads to improved
robustness to accents, background noise and technical language.

## Requirements

- Python 3.9+
- ffmpeg

## Installation

```bash
pip install git+https://github.com/dsymbol/decipher
```

## Command-line usage

General command line usage help:

```bash
$ decipher transcribe --help
usage: decipher transcribe [-h] -i  [-o] [--model {tiny.en,tiny,base.en,base,small.en,small,medium.en,medium,large}] [--task {transcribe,translate}] [--subs {add,burn}]

optional arguments:
  -h, --help            show this help message and exit
  -i , --input          input video file path e.g. video.mp4
  -o , --output         output directory path
  --model {tiny.en,tiny,base.en,base,small.en,small,medium.en,medium,large}
                        name of the whisper model to use
  --task {transcribe,translate}
                        whether to perform X->X speech recognition ('transcribe') or X->English translation ('translate')
  --subs {add,burn}, -s {add,burn}
                        whether to perform subtitle add or burn action
```

```bash
$ decipher subtitle --help
usage: decipher subtitle [-h] -i  [-o] --subs  [--task {add,burn}]

optional arguments:
  -h, --help         show this help message and exit
  -i , --input       input video file path e.g. video.mp4
  -o , --output      output directory path
  --subs , -s        input subtitles path e.g. subtitle.srt
  --task {add,burn}  whether to perform subtitle add or burn action
```

#### Examples

Generate SRT subtitles for video

```bash
decipher transcribe -i video.mp4 --model small
```

Burn generated subtitles into video

```bash
decipher subtitle -i video.mp4 -s video.srt --task burn
```

Together without validating transcription
```bash
decipher transcribe -i video.mp4 --model small --subs burn
```