import os
import json
import base64
import requests

API_KEY = os.getenv("GNANI_API_KEY")
URL = "https://api.vachana.ai/api/v1/tts/sse"

with open("turns.json", "r", encoding="utf-8") as f:
    turns = json.load(f)

for i, turn in enumerate(turns):
    turn_id = f"t{i + 1}"
    text = turn["text"]
    who = turn["who"]

    # Different voice for scammer and victim
    voice = "Shubham" if who == "scammer" else "Chetana"

    payload = {
        "model": "timbre-v3.0",
        "voice": voice,
        "text": text,
        "audio_config": {
            "sample_rate": 44100,
            "num_channels": 1,
            "sample_width": 2,
            "encoding": "linear_pcm",
            "container": "wav"
        }
    }

    print(f"Generating {turn_id} ({who})...")

    response = requests.post(
        URL,
        json=payload,
        headers={
            "X-API-Key-ID": API_KEY,
            "Content-Type": "application/json"
        },
        timeout=60
    )

    if response.status_code != 200:
        print(f"ERROR generating {turn_id}:")
        print(response.text)
        continue

    filename = f"audio/{turn_id}.wav"

    with open(filename, "wb") as f:
        for line in response.text.splitlines():

            if line.startswith("data:"):
                data = line.replace("data:", "").strip()

                if data.startswith("{"):
                    event = json.loads(data)

                    if event.get("audio"):
                        audio_data = base64.b64decode(event["audio"])
                        f.write(audio_data)

    print(f"Saved: {filename}")

print("\nAll audio generation completed.")