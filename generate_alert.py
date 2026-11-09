import os
import json
import base64
import requests

API_KEY = os.getenv("GNANI_API_KEY")

URL = "https://api.vachana.ai/api/v1/tts/sse"

payload = {
    "model": "timbre-v3.0",
    "voice": "Chetana",
    "text": "सावधान। यह scam call है। OTP बिलकुल मत दीजिए। Call काट दीजिए।",
    "audio_config": {
        "sample_rate": 44100,
        "num_channels": 1,
        "sample_width": 2,
        "encoding": "linear_pcm",
        "container": "wav"
    }
}

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
    print("ERROR:")
    print(response.text)
    exit()

with open("audio/alert.wav", "wb") as f:

    for line in response.text.splitlines():

        if line.startswith("data:"):

            data = line.replace("data:", "").strip()

            if data.startswith("{"):

                event = json.loads(data)

                if event.get("audio"):
                    audio_data = base64.b64decode(event["audio"])
                    f.write(audio_data)

print("✅ alert.wav generated successfully")