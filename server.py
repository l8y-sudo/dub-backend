"""
سيرفر TTS بسيط باستخدام edge-tts (صوت Microsoft Edge الاحترافي، مجاني بالكامل).

تشغيل محلي:
    pip install -r requirements.txt
    uvicorn server:app --host 0.0.0.0 --port 8000

نشر مجاني:
    Render.com أو Railway.app — راجع ملف README.md للتفاصيل.
"""

import asyncio
import io
import logging

import edge_tts
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("dub-tts")

app = FastAPI(title="Dubbing TTS Backend")

# يسمح لأي صفحة HTML (حتى لو مفتوحة محلياً كملف file://) بالاتصال بالسيرفر.
# لو نشرت الصفحة على دومين معروف، تقدر تحصر allow_origins فيه فقط لمزيد من الأمان.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# أصوات إسبانية حقيقية من Microsoft Edge — جودة عالية جداً وقريبة من الصوت البشري
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

MAX_CHARS = 8000  # حد أمان معقول لكل طلب واحد


@app.get("/")
def root():
    return {"status": "ok", "voices": list(VOICES.keys())}


@app.get("/voices")
def list_voices():
    return VOICES


class TTSRequest(BaseModel):
    text: str
    voice: str = "es-ES-male"
    rate: str = "+0%"


@app.post("/tts")
async def tts(body: TTSRequest):
    text = body.text
    voice = body.voice
    rate = body.rate
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="النص فارغ")
    if len(text) > MAX_CHARS:
        raise HTTPException(
            status_code=413,
            detail=f"النص طويل جداً ({len(text)} حرف) — الحد الأقصى {MAX_CHARS}",
        )

    edge_voice = VOICES.get(voice, voice)  # يسمح أيضاً بتمرير اسم الصوت الكامل مباشرة
    log.info("TTS request: voice=%s chars=%d", edge_voice, len(text))

    audio_chunks: list[bytes] = []
    try:
        communicate = edge_tts.Communicate(text, edge_voice, rate=rate)
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])
    except Exception as e:
        log.exception("فشل توليد الصوت")
        raise HTTPException(status_code=502, detail=f"فشل توليد الصوت: {e}")

    if not audio_chunks:
        raise HTTPException(status_code=502, detail="لم يتم توليد أي صوت (تحقق من اسم الصوت)")

    audio_bytes = b"".join(audio_chunks)
    return StreamingResponse(
        io.BytesIO(audio_bytes),
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline; filename=dub.mp3"},
    )


@app.get("/health")
def health():
    return {"status": "healthy"}
