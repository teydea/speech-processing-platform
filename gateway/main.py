from fastapi import FastAPI, WebSocket
import httpx
import os
import json

TTS_URL = os.getenv("TTS_URL", "http://tts:8082")

app = FastAPI()

@app.websocket("/ws/tts")
async def proxy_tts(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        payload = json.loads(data)
        
        if "text" in payload:
            text = payload["text"]
        elif "segments" in payload:
            text = " ".join(seg["text"] for seg in payload["segments"])
        else:
            await websocket.send_text('{"error": "invalid format"}')
            return

        async with httpx.AsyncClient(timeout=60.0) as client:
            await websocket.send_text('{"error": "HTTP TTS not implemented yet. Use direct TTS for now."}')
            return

    except Exception as e:
        await websocket.send_text(f'{{"error": "{str(e)}"}}')
    finally:
        await websocket.close()