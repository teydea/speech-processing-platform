# client/echo_bytes.py
import requests
import wave
import sys

with wave.open("input.wav", "rb") as wf:
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
        print("Ошибка: нужен mono, 16-bit, 16kHz WAV")
        sys.exit(1)
    audio_bytes = wf.readframes(wf.getnframes())

print("Распознаём речь через gateway...")
asr_resp = requests.post(
    "http://localhost:8000/api/stt/bytes",
    params={"sr": 16000, "ch": 1},
    data=audio_bytes
)

if asr_resp.status_code != 200:
    print("Ошибка ASR:", asr_resp.text)
    sys.exit(1)

asr_data = asr_resp.json()
recognized_text = asr_data.get("text", "")
print("Распознанный текст:", recognized_text)

segments = asr_data.get("segments", [])
if segments:
    print("Сегменты:")
    for seg in segments:
        print(f"  [{seg['start_ms']}–{seg['end_ms']} ms]: {seg['text']}")

print("\n→ Синтезируем речь (echo)...")
response = requests.post(
    "http://localhost:8000/api/echo-bytes",
    params={"sr": 16000, "ch": 1, "fmt": "s16le"},
    data=audio_bytes,
    stream=True
)

if response.status_code != 200:
    print("Ошибка TTS:", response.text)
    sys.exit(1)

with open("out_echo.wav", "wb") as f:
    for chunk in response.iter_content(chunk_size=4096):
        f.write(chunk)

print("Готово! Аудио сохранено в out_echo.wav")