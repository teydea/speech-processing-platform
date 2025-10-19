# gateway/main.py
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import StreamingResponse, JSONResponse
import httpx
import json
import os

app = FastAPI()

TTS_URL = os.getenv("TTS_URL", "http://tts:8082")
ASR_URL = os.getenv("ASR_URL", "http://asr:8081")


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
            async with client.stream("POST", f"{TTS_URL}/api/tts", json={"text": text}) as resp:
                if resp.status_code != 200:
                    await websocket.send_text(f'{{"error": "TTS failed: {resp.status_code}"}}')
                    return

                async for chunk in resp.aiter_bytes():
                    await websocket.send_bytes(chunk)

                await websocket.send_text('{"type": "end"}')

    except Exception as e:
        await websocket.send_text(f'{{"error": "{str(e)}"}}')
    finally:
        await websocket.close()


@app.post("/api/stt/bytes")
async def proxy_stt(request: Request):
    sr = request.query_params.get("sr")
    ch = request.query_params.get("ch")
    body = await request.body()
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{ASR_URL}/api/stt/bytes",
            params={"sr": sr, "ch": ch},
            content=body
        )
        return JSONResponse(resp.json(), status_code=resp.status_code)


@app.post("/api/echo-bytes")
async def echo_bytes(request: Request):
    sr = request.query_params.get("sr", "16000")
    ch = request.query_params.get("ch", "1")

    body = await request.body()

    # 1. ASR
    async with httpx.AsyncClient(timeout=30.0) as client:
        asr_resp = await client.post(
            f"{ASR_URL}/api/stt/bytes",
            params={"sr": sr, "ch": ch},
            content=body
        )
        if asr_resp.status_code != 200:
            return JSONResponse(asr_resp.json(), status_code=asr_resp.status_code)
        stt_result = asr_resp.json()
        text = stt_result.get("text", "")

    # 2. TTS
    async with httpx.AsyncClient(timeout=60.0) as client:
        tts_resp = await client.post(
            f"{TTS_URL}/api/tts",
            json={"text": text}
        )
        if tts_resp.status_code != 200:
            error_detail = await tts_resp.aread()
            return JSONResponse({"error": "TTS failed", "detail": error_detail.decode()}, status_code=500)

        async def stream_audio():
            async for chunk in tts_resp.aiter_bytes():
                yield chunk

        return StreamingResponse(stream_audio(), media_type="application/octet-stream")