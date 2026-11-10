"""Run Gnani Prisma on each generated audio file ONCE and cache the real transcripts.

Usage:  export GNANI_API_KEY="..."   then   python make_transcripts.py
Output: transcripts.json  (a list of 8 strings, one per turn, in order)
"""
import json
import os
import requests

KEY = os.environ["GNANI_API_KEY"]
N_TURNS = len(json.load(open("turns.json", encoding="utf-8")))


def transcribe(path):
    with open(path, "rb") as f:
        r = requests.post(
            "https://api.vachana.ai/stt/v3",
            headers={"X-API-Key-ID": KEY},
            files={"audio_file": (os.path.basename(path), f, "audio/wav")},
            data={"model": "prisma-v3.0", "language_code": "indic-auto"},
            timeout=60,
        )
    r.raise_for_status()
    return r.json()["transcript"]


out = []
for i in range(1, N_TURNS + 1):
    text = transcribe(f"audio/t{i}.wav")
    print(f"t{i}: {text}")
    out.append(text)

with open("transcripts.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("\nSaved transcripts.json")