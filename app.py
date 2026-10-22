
#!/usr/bin/env python3
"""Lokalna transkrypcja Whisper + diaryzacja pyannote.audio."""

import argparse
import gc
import json
import os
import sys
from pathlib import Path


def timestamp(seconds: float, srt: bool = False) -> str:
    ms = max(0, round(seconds * 1000))
    hours, ms = divmod(ms, 3_600_000)

    minutes, ms = divmod(ms, 60_000)
    secs, ms = divmod(ms, 1000)
    sep = "," if srt else "."
    return f"{hours:02}:{minutes:02}:{secs:02}{sep}{ms:03}"


def assign_speaker(start, end, turns):
    """Przypisz mówcę na podstawie największego nakładania czasu."""
    overlaps = {}
    for turn_start, turn_end, speaker in turns:
        overlap = max(
            0.0, min(end, turn_end) - max(start, turn_start)
        )
        if overlap > 0:
            overlaps[speaker] = overlaps.get(speaker, 0.0) + overlap

    if not overlaps:
        return "UNKNOWN"

    speaker = max(overlaps, key=overlaps.get)
    # speaker_0 -> SPEAKER_00
    if speaker.startswith("speaker_"):
        suffix = speaker.split("_")[-1]
        if suffix.isdigit():
            return f"SPEAKER_{int(suffix):02d}"
    return speaker.upper()


def main():
    parser = argparse.ArgumentParser(
        description="Whisper ASR + diarizacja mówców na GPU"
    )
    parser.add_argument("audio", help="Ścieżka do nagrania")
    parser.add_argument(
        "--model", default="large-v3-turbo",
        help="Model Whisper, np. large-v3-turbo, medium, small"
    )
    parser.add_argument(
        "--language", default="pl",
        help="Kod języka, np. pl, en; auto oznacza wykrywanie"
    )
    parser.add_argument(
        "--device", choices=["auto", "cuda", "cpu"], default="auto"
    )
    parser.add_argument(
        "--compute", default=None,
        help="Typ obliczeń faster-whisper, np. float16 lub int8_float16"
    )
    parser.add_argument(
        "--num-speakers", type=int, default=None,
        help="Znana liczba rozmówców (opcjonalnie)"
    )
    parser.add_argument(
        "--output", default=None,
        help="Katalog wyników (domyślnie katalog nagrania)"
    )
    args = parser.parse_args()

    audio = Path(args.audio).expanduser().resolve()
    if not audio.is_file():
        parser.error(f"Nie znaleziono pliku: {audio}")

    try:
        import torch
        from faster_whisper import WhisperModel
        from pyannote.audio import Pipeline
    except ImportError as exc:
        sys.exit(
            f"Brak biblioteki: {exc}\n"
            "Aktywuj .venv i zainstaluj wymagane pakiety."
        )

    cuda = torch.cuda.is_available()
    if args.device == "cuda" and not cuda:
        sys.exit("Wybrano CUDA, ale PyTorch nie wykrywa GPU.")
    use_gpu = cuda and args.device != "cpu"
    device = "cuda" if use_gpu else "cpu"
    compute = args.compute or ("float16" if use_gpu else "int8")
    language = None if args.language.lower() == "auto" else args.language

    outdir = Path(args.output).expanduser() if args.output else audio.parent
    outdir.mkdir(parents=True, exist_ok=True)
    stem = audio.stem

    print(f"Nagranie: {audio}")
    print(f"Urządzenie: {device}; model Whisper: {args.model}")
    if use_gpu:
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    # ETAP 1: transkrypcja
    print("\n[1/2] Transkrypcja Whisper...")
    asr = WhisperModel(
        args.model,
        device=device,
        compute_type=compute,
    )
    segments_iter, info = asr.transcribe(
        str(audio),
        language=language,
        beam_size=5,
        vad_filter=True,
        word_timestamps=False,
    )

    segments = []
    for seg in segments_iter:
        segments.append({
            "start": float(seg.start),
            "end": float(seg.end),
            "text": seg.text.strip(),
        })

    detected_language = info.language
    print(f"Język: {detected_language}; segmenty: {len(segments)}")

    # Zwolnij pamięć przed załadowaniem modelu diaryzacji.
    del asr, segments_iter
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # ETAP 2: diaryzacja
    print("\n[2/2] Rozpoznawanie rozmówców...")
    token = os.environ.get("HF_TOKEN")
    if not token:
        sys.exit(
            "Brak HF_TOKEN. Ustaw token Hugging Face w środowisku."
        )

    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-community-1",
        token=token,
    )
    if use_gpu:
        pipeline.to(torch.device("cuda"))

    kwargs = {}
    if args.num_speakers is not None:
        kwargs["num_speakers"] = args.num_speakers

    result = pipeline(str(audio), **kwargs)

    # Community-1 udostępnia exclusive diarization,
    # co ułatwia dopasowanie mówców do transkrypcji.
    annotation = getattr(
        result, "exclusive_speaker_diarization", None
    )
    if annotation is None:
        annotation = result.speaker_diarization

    turns = []
    for turn, _, speaker in annotation.itertracks(yield_label=True):
        turns.append((float(turn.start), float(turn.end), str(speaker)))

    for seg in segments:
        seg["speaker"] = assign_speaker(
            seg["start"], seg["end"], turns
        )

    # TXT
    txt_path = outdir / f"{stem}.txt"
    with txt_path.open("w", encoding="utf-8") as f:
        for seg in segments:
            f.write(
                f"[{timestamp(seg['start'])} - "
                f"{timestamp(seg['end'])}] "
                f"{seg['speaker']}: {seg['text']}\n"
            )

    # SRT
    srt_path = outdir / f"{stem}.srt"
    with srt_path.open("w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            f.write(
                f"{i}\n"
                f"{timestamp(seg['start'], True)} --> "
                f"{timestamp(seg['end'], True)}\n"
                f"[{seg['speaker']}] {seg['text']}\n\n"
            )

    # JSON: segmenty, czasy i etykiety mówców
    json_path = outdir / f"{stem}.json"
    data = {
        "file": str(audio),
        "language": detected_language,
        "model": args.model,
        "device": device,
        "speakers": sorted({
            seg["speaker"] for seg in segments
        }),
        "segments": segments,
        "diarization": [
            {
                "start": start,
                "end": end,
                "speaker": speaker,
            }
            for start, end, speaker in turns
        ],
    }
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\nGotowe! Wyniki zapisano w:")
    print(f"  TXT:  {txt_path}")
    print(f"  SRT:  {srt_path}")
    print(f"  JSON: {json_path}")


if __name__ == "__main__":
    main()
