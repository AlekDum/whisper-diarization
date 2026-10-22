import os
import time
import subprocess
from pathlib import Path

import gradio as gr

BASE_DIR = Path(__file__).resolve().parent
PYTHON = BASE_DIR / ".venv" / "bin" / "python"
APP = BASE_DIR / "app.py"


def run_transcription(audio, model, language, device, compute, num_speakers):
    if not audio:
        yield "Najpierw wybierz plik audio.", ""
        return

    output_dir = BASE_DIR / "wyniki-gui"
    output_dir.mkdir(parents=True, exist_ok=True)

    command = [
        str(PYTHON), "-u", str(APP), str(audio),
        "--device", device,
        "--model", model,
        "--language", language,
        "--compute", compute,
        "--output", str(output_dir),
    ]

    if num_speakers and int(num_speakers) > 0:
        command += ["--num-speakers", str(int(num_speakers))]

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    start = time.monotonic()
    log = ""

    try:
        process = subprocess.Popen(
            command,
            cwd=str(BASE_DIR),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        while True:
            line = process.stdout.readline()

            if line:
                log += line
                elapsed = int(time.monotonic() - start)
                yield f"Przetwarzanie — {elapsed} s\n\n{log}", ""
            elif process.poll() is not None:
                break
            else:
                time.sleep(0.2)

        rest = process.stdout.read()
        if rest:
            log += rest

        elapsed = int(time.monotonic() - start)
        if process.returncode == 0:
            message = f"Zakończono. Czas pracy: {elapsed} s"
        else:
            message = f"Błąd programu (kod {process.returncode}). Czas: {elapsed} s"

        files = [
            str(f) for f in sorted(output_dir.iterdir())
            if f.is_file()
        ]
        file_list = "\n".join(files) if files else "Brak plików wynikowych."

        yield f"{message}\n\n{log}", file_list

    except Exception as exc:
        yield f"Błąd uruchamiania: {exc}\n\n{log}", ""


with gr.Blocks(title="Whisper — transkrypcja i diarizacja") as demo:
    gr.Markdown(
        "# Transkrypcja i diarizacja nagrań\n"
        "Wybierz plik audio i ustaw parametry przetwarzania."
    )

    audio = gr.Audio(
        label="Nagranie audio",
        type="filepath",
        sources=["upload"],
    )

    with gr.Row():
        model = gr.Dropdown(
            ["small", "medium", "large-v3-turbo"],
            value="small",
            label="Model Whisper",
        )
        language = gr.Dropdown(
            ["auto", "pl", "ru", "en"],
            value="ru",
            label="Język nagrania",
        )

    with gr.Row():
        device = gr.Radio(
            ["cpu", "cuda"],
            value="cpu",
            label="Urządzenie",
        )
        compute = gr.Dropdown(
            ["int8", "float32", "float16", "int8_float16"],
            value="int8",
            label="Typ obliczeń",
        )
        speakers = gr.Number(
            value=0,
            precision=0,
            minimum=0,
            label="Liczba rozmówców (0 = automatycznie)",
        )

    start_button = gr.Button("Uruchom transkrypcję", variant="primary")
    status = gr.Textbox(
        label="Postęp i komunikaty",
        lines=16,
        max_lines=30,
        interactive=False,
    )
    results = gr.Textbox(
        label="Pliki wynikowe",
        lines=5,
        interactive=False,
    )

    start_button.click(
        fn=run_transcription,
        inputs=[audio, model, language, device, compute, speakers],
        outputs=[status, results],
    )

if __name__ == "__main__":
    demo.queue().launch(
        server_name="127.0.0.1",
        server_port=7860,
        inbrowser=True,
    )
