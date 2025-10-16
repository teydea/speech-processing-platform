from fastapi import FastAPI, Request
from faster_whisper import WhisperModel
import os
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("asr")

app = FastAPI()

model_size = os.getenv("MODEL_NAME", "base.en")
sample_rate = int(os.getenv("SAMPLE_RATE", 16000))

logger.info(f"Loading ASR model: {model_size}")
asr_model = WhisperModel(model_size, device="cpu", compute_type="int8")
logger.info("ASR model loaded.")

@app.post("/api/stt/bytes")
async def stt_bytes(request: Request):
    body = await request.body()
    
    sr = int(request.query_params.get("sr", sample_rate))
    ch = int(request.query_params.get("ch", 1))

    if len(body) == 0:
        return {"error": "empty audio"}

    audio_int16 = np.frombuffer(body, dtype=np.int16)
    audio_float32 = audio_int16.astype(np.float32) / 32767.0

    duration = len(audio_float32) / sr
    if duration > 15:
        return {"error": "audio too long (>15s)"}

    segments, _ = asr_model.transcribe(audio_float32, language="en")

    full_text = " ".join(seg.text.strip() for seg in segments)
    segs = [
        {
            "start_ms": int(seg.start * 1000),
            "end_ms": int(seg.end * 1000),
            "text": seg.text.strip()
        }
        for seg in segments
    ]

    return {"text": full_text.strip(), "segments": segs}