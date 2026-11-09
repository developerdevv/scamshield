import os
import json
import requests
from brain import calculate_risk

API_KEY = os.getenv("GNANI_API_KEY")

with open("turns.json", "r", encoding="utf-8") as f:
    turns = json.load(f)

conversation = []

for i, turn in enumerate(turns):
    turn_id = f"t{i + 1}"
    audio_path = f"audio/{turn_id}.wav"

    print(f"\n--- {turn_id} ({turn['who']}) ---")

    # Prisma STT
    with open(audio_path, "rb") as audio:
        response = requests.post(
            "https://api.vachana.ai/stt/v3",
            headers={
                "X-API-Key-ID": API_KEY
            },
            files={
                "audio_file": (
                    f"{turn_id}.wav",
                    audio,
                    "audio/wav"
                )
            },
            data={
                "model": "prisma-v3.0",
                "language_code": "indic-auto",
                "format": "transcribe"
            },
            timeout=60
        )

    result = response.json()

    if not result.get("success"):
        print("STT ERROR:", result)
        continue

    transcript = result["transcript"]

    conversation.append({
        "who": turn["who"],
        "text": transcript
    })

    print("Transcript:", transcript)

    # Local risk analysis
    risk = calculate_risk(conversation)

    print(f"Risk: {risk['risk_score']}%")
    print(f"Level: {risk['risk_level']}")
    print(f"Tactics: {', '.join(risk['tactics'])}")

    if risk["warning"]:
        print(f"⚠️ WARNING: {risk['warning']}")

print("\n=== PIPELINE COMPLETE ===")