from fastapi import FastAPI, WebSocket
from TTS.api import TTS
from fastapi import WebSocket, Request, Response
import os
import logging
import json
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tts")

app = FastAPI()

model_name = os.getenv("MODEL_NAME", "en/ljspeech/tacotron2-DDC")
logger.info(f"Loading TTS model: {model_name}")
tts_model = TTS(model_name=model_name, progress_bar=False, gpu=False)
logger.info("TTS model loaded successfully.")

@app.websocket("/ws/tts")
async def tts_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        payload = json.loads(data)
        text = payload.get("text", "").strip()
        
        if not text:
            await websocket.send_text('{"error": "empty text"}')
            return

        logger.info(f"Generating speech for: {text[:50]}...")

        wav = tts_model.tts(text)

        wav = np.array(wav)
        wav = (wav * 32767).astype(np.int16)
        audio_bytes = wav.tobytes()

        await websocket.send_bytes(audio_bytes)
        await websocket.send_text('{"type": "end"}')

    except Exception as e:
        logger.error(f"TTS error: {e}")
        await websocket.send_text(f'{{"error": "{str(e)}"}}')
    finally:
        await websocket.close()

from fastapi.responses import StreamingResponse

@app.post("/api/tts")
async def tts_http(request: Request):
    data = await request.json()
    text = data.get("text", "").strip()
    if not text:
        return {"error": "empty text"}

    logger.info(f"TTS HTTP input: {text}")
    wav = tts_model.tts(text)

    wav = np.array(wav)
    wav = (wav * 32767).astype(np.int16)
    audio_bytes = wav.tobytes()

    return Response(content=audio_bytes, media_type="application/octet-stream")