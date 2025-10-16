import requests
import wave
import sys

with wave.open("input.wav", "rb") as wf:
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
        print("Ошибка: нужен mono, 16-bit, 16kHz WAV")
        sys.exit(1)
    audio_bytes = wf.readframes(wf.getnframes())

print("Отправка аудио в STT...")
response = requests.post(
    "http://localhost:8081/api/stt/bytes",
    params={"sr": 16000, "ch": 1},
    data=audio_bytes
)

if response.status_code != 200:
    print("Ошибка STT:", response.text)
    sys.exit(1)

stt_result = response.json()
text = stt_result["text"]
print(f"Распознано: {text}")

print("Отправка текста в TTS...")
response = requests.post(
    "http://localhost:8082/api/tts",
    json={"text": text}
)

if response.status_code != 200:
    print("Ошибка TTS:", response.text)
    sys.exit(1)

with open("out_echo.wav", "wb") as f:
    f.write(response.content)

print("Готово! Аудио сохранено в out_echo.wav")