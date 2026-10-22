# Whisper Diarization — transkrypcja i diarizacja

Lokalny program do transkrypcji nagrań audio oraz przypisywania
fragmentów wypowiedzi do rozmówców.

Projekt powstał w środowisku Kali Linux z wykorzystaniem Pythona,
faster-whisper, pyannote.audio i Gradio.

## Funkcje

- Transkrypcja nagrań za pomocą faster-whisper.
- Obsługa modeli Whisper, w tym large-v3-turbo.
- Wybór języka nagrania lub automatyczne wykrywanie języka.
- Diarizacja rozmówców przez pyannote.audio.
- Opcjonalne podanie znanej liczby rozmówców.
- Zapis wyników do TXT, SRT i JSON.
- Interfejs graficzny oparty na Gradio.
- Możliwość pracy na CPU lub kompatybilnym GPU CUDA.

## Jak działa program?

1. Wczytuje nagranie audio.
2. Wykonuje transkrypcję i zapisuje segmenty tekstu z czasami.
3. Uruchamia model diarizacji pyannote.audio.
4. Dopasowuje etykiety rozmówców do segmentów transkrypcji.
5. Zapisuje wyniki w trzech formatach.

Przypisanie rozmówcy do segmentu tekstu opiera się na nakładaniu
przedziałów czasowych. Wyniki mogą wymagać ręcznej weryfikacji.

## Pliki projektu

- app.py — główny program transkrypcji i diarizacji.
- gui.py — interfejs graficzny Gradio.
- requirements.txt — zależności Pythona.
- docs/ — dokumentacja edukacyjna.

## Wymagania

- Linux.
- Python zgodny z używanymi bibliotekami.
- FFmpeg lub inne wymagania audio zależne od środowiska.
- Biblioteki wymienione w requirements.txt.
- Token Hugging Face wymagany przez używany model diarizacji.
- Dostęp do modelu pyannote/speaker-diarization-community-1.

Warunki dostępu do modelu należy zaakceptować na stronie Hugging Face,
jeśli wymaga tego jego aktualna konfiguracja.

## Uruchamianie interfejsu graficznego

W katalogu projektu wykonaj:

    ./.venv/bin/python gui.py

Interfejs powinien być dostępny lokalnie pod adresem:

    http://127.0.0.1:7860

## Uruchamianie z terminala

Przykład dla nagrania rosyjskiego:

    ./.venv/bin/python app.py "/ścieżka/do/nagrania.ogg" \
      --model large-v3-turbo \
      --language ru \
      --device cpu \
      --compute int8 \
      --output ./wyniki

Diarizacja wymaga zmiennej środowiskowej HF_TOKEN.
Nie umieszczaj tokenu bezpośrednio w kodzie ani w repozytorium.

## Formaty wynikowe

- TXT — segmenty tekstu z czasami i etykietami rozmówców.
- SRT — napisy z czasami i etykietami rozmówców.
- JSON — segmenty, język, model, urządzenie i dane diarizacji.

## Ograniczenia

- Jakość transkrypcji zależy od nagrania i wybranego modelu.
- Nakładające się wypowiedzi mogą utrudniać przypisanie rozmówców.
- Etykiety SPEAKER_00, SPEAKER_01 itd. nie identyfikują prawdziwych osób.
- Czas przetwarzania zależy od długości nagrania i sprzętu.

## Bezpieczeństwo i prywatność

Nie publikuj tokenów, prywatnych nagrań ani wyników zawierających
dane osobowe bez odpowiedniej zgody.

## Status dokumentacji

Dokumentacja jest przygotowywana na podstawie istniejącego kodu.
Instrukcje instalacji na innych systemach wymagają osobnego testu.

## Licencje

Przed publikacją należy określić licencję własnego kodu oraz sprawdzić
warunki licencyjne bibliotek, modeli i przykładowych nagrań.
