# Dubbing TTS Backend

سيرفر بسيط جداً (ملف واحد) يحوّل نص إسباني إلى ملف MP3 حقيقي باستخدام
`edge-tts` — نفس محرك الأصوات المستخدم في متصفح Microsoft Edge ونظام
Windows، مجاني بالكامل بدون مفتاح API ولا حدود استخدام معروفة حتى الآن.

## لماذا سيرفر منفصل؟

خدمات TTS الاحترافية (Google, Azure, ElevenLabs) تمنع الاتصال المباشر من
المتصفح (CORS) لحماية مفاتيحها. الحل الوحيد المستقر هو سيرفر وسيط بسيط:

```
صفحة HTML  →  هذا السيرفر (Python)  →  Microsoft Edge TTS  →  ملف MP3  →  رجوع للمتصفح
```

## 1) تشغيل محلي (لتجربة سريعة على جهازك)

```bash
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8000
```

افتح في المتصفح: `http://localhost:8000/voices` للتأكد إنه شغّال.

اختبار توليد صوت مباشرة من المتصفح:
```
http://localhost:8000/tts?text=Hola%20mundo&voice=es-ES-male
```
يفترض يشغّل لك ملف MP3 فوراً.

## 2) النشر المجاني على Render.com (الأسهل)

1. ارفع هذا المجلد (server.py + requirements.txt) إلى مستودع GitHub جديد.
2. روح لـ https://render.com → New → Web Service → اربط المستودع.
3. الإعدادات:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn server:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free
4. بعد النشر تحصل رابط مثل: `https://your-app.onrender.com`
5. استخدم هذا الرابط داخل صفحة الدبلجة (حقل "رابط السيرفر").

⚠️ ملاحظة: الخطة المجانية في Render "تنام" بعد فترة خمول، وأول طلب بعدها
ياخذ ٣٠-٦٠ ثانية حتى يصحى. هذا طبيعي وليس خطأ.

## 3) بديل: Railway.app

نفس الخطوات تقريباً، وعندهم رصيد مجاني شهري بدل "النوم" التلقائي.

## نقاط الصوت المتاحة

| المفتاح        | الصوت              | اللهجة      |
|----------------|--------------------|--------------| 
| es-ES-male     | AlvaroNeural       | إسبانيا (رجل) |
| es-ES-female   | ElviraNeural       | إسبانيا (امرأة) |
| es-MX-male     | JorgeNeural        | المكسيك (رجل) |
| es-MX-female   | DaliaNeural        | المكسيك (امرأة) |
| es-AR-male     | TomasNeural        | الأرجنتين (رجل) |
| es-AR-female   | ElenaNeural        | الأرجنتين (امرأة) |
| es-US-male     | AlonsoNeural       | أمريكا اللاتينية (رجل) |
| es-US-female   | PalomaNeural       | أمريكا اللاتينية (امرأة) |

كل هذه أصوات Neural حقيقية من Microsoft، جودتها قريبة جداً من الصوت البشري.
