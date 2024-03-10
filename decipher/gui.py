import os

import gradio as gr
from decipher import action

from tempfile import mktemp, gettempdir


def __transcribe(video_in, model, language, task, batch_size, subs):
    result = action.transcribe(
        video_in,
        gettempdir(),
        model,
        language if language else None,
        task.lower(),
        batch_size,
        subs.lower() if subs else None
    )
    with open(result.subtitle_file, "r", encoding='utf-8') as f:
        subtitles = f.read()
    return subtitles, result.video_file


def __subtitle(video_in, subs, task):
    temp_srt = mktemp(suffix=".srt")
    with open(temp_srt, "w", encoding="utf-8") as f:
        f.write(subs)
    result = action.subtitle(video_in, temp_srt, gettempdir(), task.lower())
    os.remove(temp_srt)
    return result.video_file


MODELS = ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"]


def ui():
    with gr.Blocks() as demo:
        with gr.Tab("Transcribe"):
            with gr.Row():
                with gr.Column():
                    ti_video = gr.Video(label="Video", sources=["upload"])
                    ti_model = gr.Dropdown(choices=MODELS, value="medium", label="Model")
                    ti_language = gr.Textbox(
                        label="Language", placeholder="English",
                        info="Language spoken in the audio leave empty for detection"
                    )
                    ti_task = gr.Radio(
                        choices=["Transcribe", "Translate"], value="Transcribe", label="Task",
                        info="Whether to perform X->X speech recognition or X->English translation"
                    )
                    ti_subtitles = gr.Radio(
                        label="Subtitle video", choices=["Add", "Burn"],
                        info="Whether to perform subtitle add or burn action leave empty for none"
                    )
                    ti_batch_size = gr.Slider(
                        0, 24, value=24, step=1, label="Batch Size",
                        info="Number of parallel batches reduce if you face out of memory errors"
                    )
                with gr.Column():
                    to_subtitles = gr.Textbox(label="Subtitles", lines=15, show_copy_button=True, autoscroll=False)
                    to_video = gr.Video(label="Video")
            transcribe_btn = gr.Button("Transcribe")
            transcribe_btn.click(fn=__transcribe,
                                 inputs=[ti_video, ti_model, ti_language, ti_task, ti_batch_size, ti_subtitles],
                                 outputs=[to_subtitles, to_video])

        with gr.Tab("Subtitle"):
            with gr.Row():
                with gr.Column():
                    si_video = gr.Video(label="Video", sources=["upload"])
                    si_subtitles = gr.Textbox(label="Subtitles", lines=15, show_copy_button=True)
                    si_task = gr.Radio(
                        label="Subtitle video", choices=["Add", "Burn"], value="Burn",
                        info="Whether to perform subtitle add or burn action leave empty for none"
                    )
                with gr.Column():
                    so_video = gr.Video(label="Video")

            subtitle_btn = gr.Button("Subtitle")
            subtitle_btn.click(fn=__subtitle, inputs=[si_video, si_subtitles, si_task], outputs=so_video)

    return demo
