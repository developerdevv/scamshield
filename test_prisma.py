import os
import requests

API_KEY = os.getenv("GNANI_API_KEY")

with open("audio/scammer_01.wav", "rb") as f:
    response = requests.post(
        "https://api.vachana.ai/stt/v3",
        headers={
            "X-API-Key-ID": API_KEY
        },
        files={
            "audio_file": ("scammer_01.wav", f, "audio/wav")
        },
        data={
            "model": "prisma-v3.0",
            "language_code": "indic-auto",
            "format": "transcribe"
        },
        timeout=60
    )

print(response.json())