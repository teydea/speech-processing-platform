# Streaming TTS + Offline STT Pipeline

## Требования
- Docker и Docker Compose;
- Python 3.8+ (для клиентов и тестов)

## Запуск сервисов

1. Скопируйте переменные окружения:

```bash
cp .env.example .env
```

2. Запустите сервисы
```bash
docker-compose up --build
```

Сервисы будут доступны:
- **Gateway**: `http://localhost:8000`
  - WebSocket: `ws://localhost:8000/ws/tts`
  - HTTP: `POST /api/echo-bytes`
- **TTS (внутри сети)**: `http://tts:8082`
- **ASR (внутри сети)**: `http://asr:8081`

## Локальное тестирование

Клиенты (e2e тестирование)

Стриминг TTS:
```bash
python client/stream_tts.py
```

Полный цикл ASR -> TTS:
Подготовьте client/input.wav (моно, 16-bit, 16kHz, <15 сек), затем
```bash
python client/echo_bytes.py
```

## Unit-тесты
Для запуска unit-тестов требуется установка зависимостей:
```bash
python -m venv .venv
.venv\Scripts\activate

pip install fastapi uvicorn[standard] pytest httpx

cd tts-service && python -m pytest tests/ -v && cd ..
cd asr-service && python -m pytest tests/ -v && cd ..
```

Тесты покрывают пограничные случаи: пустой текст (TTS), пустое/слишком длинное аудио (ASR).

## Архитектура
tts-service: стриминговый TTS на основе Coqui TTS (tacotron2-DDC)
asr-service: STT по raw PCM с использованием faster-whisper/base.en
gateway: единая точка входа, проксирует запросы и реализует /api/echo-bytes
client/: скрипты для end-to-end проверки

## Документация
Подробнее о принятых решениях -- см. DECISIONS.md.
