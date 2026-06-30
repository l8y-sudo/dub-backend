import asyncio
import io
import logging

import edge_tts
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("dub-tts")

app = FastAPI(title="Dubbing TTS Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

VOICES = {
    "es-ES-male": "es-ES-AlvaroNeural",
    "es-ES-female": "es-ES-ElviraNeural",
    "es-MX-male": "es-MX-JorgeNeural",
    "es-MX-female": "es-MX-DaliaNeural",
    "es-AR-male": "es-AR-TomasNeural",
    "es-AR-female": "es-AR-ElenaNeural",
    "es-US-male": "es-US-AlonsoNeural",
    "es-US-female": "es-US-PalomaNeural",
}

@app.get("/")
def root():
    return {"status": "ok", "voices": list(VOICES.keys())}

@app.get("/voices")
def list_voices():
    return VOICES

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/tts")
async def tts(
    text: str = Query(...),
    voice: str = Query("es-ES-male"),
    rate: str = Query("+0%"),
):
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="النص فارغ")
    if len(text) > 8000:
        raise HTTPException(status_code=413, detail="النص طويل جداً")

    edge_voice = VOICES.get(voice, voice)
    log.info("TTS: voice=%s chars=%d", edge_voice, len(text))

    chunks = []
    try:
        communicate = edge_tts.Communicate(text, edge_voice, rate=rate)
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                chunks.append(chunk["data"])
    except Exception as e:
        log.exception("فشل")
        raise HTTPException(status_code=502, detail=str(e))

    if not chunks:
        raise HTTPException(status_code=502, detail="لم يتم توليد صوت")

    return StreamingResponse(
        io.BytesIO(b"".join(chunks)),
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline; filename=dub.mp3"},
  )
