<div align="center">
<h1>Decipher 📺️</h1>
<img src="https://user-images.githubusercontent.com/88138099/195132806-0ac06b96-8989-47d0-ba99-39cb808938d2.png"/>
</div>

Effortlessly burn [openai/whisper](https://github.com/openai/whisper) AI generated transcription subtitles into provided
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
pip install git+https://github.com/openai/whisper.git 
```

## Command-line usage

```
usage: decipher [-h] [--model {tiny.en,tiny,base.en,base,small.en,small,medium.en,medium,large}] [--task {transcribe,translate}] video 

Transcribe videos easily using openai's whisper

positional arguments:
  video                 input video path e.g. video.mp4

optional arguments:
  -h, --help            show this help message and exit
  --model {tiny.en,tiny,base.en,base,small.en,small,medium.en,medium,large}
                        name of the whisper model to use
  --task {transcribe,translate}
                        whether to perform X->X speech recognition ('transcribe') or X->English translation ('translate')
```

#### Examples

Burn subtitles into video.mp4 using the small model

```bash
python decipher.py --model small video.mp4
```

Burn translated English subtitles into video.mp4 using the medium model

```bash
python decipher.py --model medium --task translate video.mp4
```