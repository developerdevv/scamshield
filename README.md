# 🛡️ Scam Shield

**A Hinglish scam-call escalation detector built with Gnani Prisma v3.0 and Gnani Timbre v3.**

> Demo video and post: https://x.com/dev_explains/status/2120118275397029955?a=SVw_VKN280g4iuqfbpI&s=20

## The problem
Phone scams in India, like fake CBI/police "digital arrest" calls and OTP fraud, follow the same script: a fake authority claim, then fear, then isolation ("don't tell anyone"), and finally a demand for money or an OTP. Victims usually realise only at the last step, when it is too late.

## Our solution
Scam Shield follows that escalation while a call unfolds. It transcribes each turn with Gnani Prisma, tracks which scam tactics have appeared, and shows a live risk score from 0 to 100%. At critical risk it shows a warning and speaks an alert in Hindi: *"OTP bilkul mat dijiye. Call kaat dijiye."*

## Who it is for
Everyday phone users, especially first-time digital users and elderly family members who are the usual targets of these scams. The same approach could later help banks, telecom operators and call-centre safety teams.

## How it works
1. **Gnani Timbre v3 (TTS)** generates a synthetic Hindi/Hinglish scam call with two different voices (scammer and victim), plus the spoken warning.
2. **Gnani Prisma v3.0 (STT)** transcribes every turn. The on-screen transcript is real Prisma output.
3. A **rule-based risk engine** (`brain.py`) detects five tactics: fake authority, fear/threat, isolation, money request and OTP/credential request. It accumulates risk across the call: 20% → 40% → 60% → 100%.
4. A **Streamlit app** (`app.py`) replays the call as one continuous recording and updates the transcript, risk score and warning in sync.

## Honest scope
- This replays a **synthetic** conversation turn by turn. It is **not** live call interception, and no real calls or personal data were used.
- The risk engine is rule-based keyword and tactic detection, not a machine-learning classifier.

## Run it
```bash
pip install -r requirements.txt
export GNANI_API_KEY="your-key"      # only needed to regenerate audio/transcripts
python generate_audio.py             # Timbre: creates audio/t1..t8.wav
python generate_alert.py             # Timbre: creates audio/alert.wav
python make_transcripts.py           # Prisma: creates transcripts.json
streamlit run app.py
```
Audio files and `transcripts.json` are already included, so `streamlit run app.py` works straight away.

## Team
- **Dev:** pipeline (Timbre, Prisma, risk engine) and the Streamlit app
- **Ishika:** scam scenario design, testing, demo video and post

Built for the Great Indian AI Internship Challenge by Gnani.ai. #GnaniAI
