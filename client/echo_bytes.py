# client/echo_bytes.py
import requests
import wave
import sys

with wave.open("input.wav", "rb") as wf:
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
        print("Ошибка: нужен mono, 16-bit, 16kHz WAV")
        sys.exit(1)
    audio_bytes = wf.readframes(wf.getnframes())

print("Отправка аудио в gateway /api/echo-bytes...")
response = requests.post(
    "http://localhost:8000/api/echo-bytes",
    params={"sr": 16000, "ch": 1, "fmt": "s16le"},
    data=audio_bytes,
    stream=True
)

if response.status_code != 200:
    print("Ошибка:", response.text)
    sys.exit(1)

print("Распознавание и синтез прошли успешно. Сохраняю аудио...")

with open("out_echo.wav", "wb") as f:
    for chunk in response.iter_content(chunk_size=4096):
        f.write(chunk)

print("Готово! Аудио сохранено в out_echo.wav")