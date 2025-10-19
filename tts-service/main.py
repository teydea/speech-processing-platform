# tts-service/main.py
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from TTS.api import TTS
import os
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tts")

app = FastAPI()

model_name = os.getenv("MODEL_NAME", "tts_models/en/ljspeech/tacotron2-DDC")
logger.info(f"Loading TTS model: {model_name}")
tts_model = TTS(model_name=model_name, progress_bar=False, gpu=False)
logger.info("TTS model loaded successfully.")

CHUNK_SIZE = 4096


@app.post("/api/tts")
async def tts_http(request: Request):
    try:
        data = await request.json()
        text = data.get("text", "").strip()
        if not text:
            return JSONResponse({"error": "empty text"}, status_code=400)

        logger.info(f"TTS HTTP input: {text}")
        wav = tts_model.tts(text)
        wav = np.array(wav)
        wav = (wav * 32767).astype(np.int16)
        audio_bytes = wav.tobytes()

        def iter_chunks():
            for i in range(0, len(audio_bytes), CHUNK_SIZE):
                yield audio_bytes[i:i + CHUNK_SIZE]

        return StreamingResponse(iter_chunks(), media_type="application/octet-stream")

    except Exception as e:
        logger.error(f"TTS HTTP error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)