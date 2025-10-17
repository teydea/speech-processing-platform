# client/stream_tts.py
import asyncio
import websockets
import wave
import json

async def main():
    uri = "ws://localhost:8000/ws/tts"
    
    async with websockets.connect(uri) as websocket:
        text = "Hello. This is a test of the text to speech system."
        print(f"Sending text: {text}")
        await websocket.send(json.dumps({"text": text}))

        with wave.open("out.wav", "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(22050)

            print("Receiving audio...")
            while True:
                try:
                    message = await websocket.recv()
                    if isinstance(message, str):
                        print("Control message:", message)
                        if '"type":"end"' in message or '"error"' in message:
                            break
                    else:
                        wf.writeframes(message)
                        print(f"Received {len(message)} audio bytes")
                except Exception as e:
                    print(f"Error: {e}")
                    break

        print("Audio saved to out.wav")

if __name__ == "__main__":
    asyncio.run(main())