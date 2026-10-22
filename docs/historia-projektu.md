# Historia projektu: Whisper Diarization

## Cel

Projekt służy do transkrypcji nagrań audio i przypisywania
fragmentów tekstu do rozmówców.

## Środowisko

- System: Kali Linux
- Język programowania: Python
- Środowisko wirtualne: .venv
- Interfejs użytkownika: Gradio
- Transkrypcja: faster-whisper
- Diarizacja: pyannote.audio
- Obliczenia: obecnie testowane na CPU

## Struktura projektu

### app.py

Główny program, który:
- odczytuje argumenty przekazane z terminala;
- wczytuje nagranie audio;
- wykonuje transkrypcję;
- uruchamia diarizację;
- dopasowuje etykiety rozmówców do segmentów tekstu;
- zapisuje wyniki TXT, SRT i JSON.

### gui.py

Interfejs graficzny Gradio. Umożliwia wybór pliku audio i parametrów
przetwarzania oraz wyświetla komunikaty i listę plików wynikowych.

### README.md

Główna instrukcja dla użytkowników projektu.

### requirements.txt

Lista głównych bibliotek Pythona używanych przez aplikację.

## Jak działa przetwarzanie?

1. Program sprawdza, czy plik audio istnieje.
2. faster-whisper rozpoznaje mowę i tworzy segmenty tekstu.
3. pyannote.audio wyznacza przedziały czasowe rozmówców.
4. Program dopasowuje etykiety rozmówców do segmentów na podstawie
   nakładania się przedziałów czasowych.
5. Wyniki są zapisywane w formatach TXT, SRT i JSON.

## Dostęp do modelu diarizacji

Program pobiera token z zmiennej środowiskowej HF_TOKEN.
Tokena nie należy umieszczać w kodzie ani publikować w repozytorium.

Dostęp do modelu pyannote/speaker-diarization-community-1 może
wymagać zaakceptowania warunków na stronie Hugging Face.

## Bezpieczeństwo

Nagrania, transkrypcje, wyniki, środowisko .venv i tokeny nie powinny
być publikowane razem z kodem.

Przed publikacją należy sprawdzić zawartość wszystkich plików.

## Status

Dokument powstał na podstawie analizy istniejącego kodu i sprawdzeń
wykonanych w terminalu.

Nie jest pełnym historycznym zapisem każdej czynności podczas
tworzenia programu. Kolejne etapy nauki należy dokumentować
w miarę ich weryfikowania.

## Dalsze prace

- przetestowanie instalacji na czystym środowisku;
- sprawdzenie jakości transkrypcji i diarizacji;
- przygotowanie instrukcji konfiguracji HF_TOKEN;
- sprawdzenie licencji kodu, bibliotek i modeli;
- publikacja projektu na GitHubie.
