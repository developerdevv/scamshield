# 🛡️ Scam Shield

### Synthetic scam-call detection using Gnani Timbre + Prisma

Scam Shield is a turn-by-turn synthetic scam-call detector that analyzes a simulated scam conversation and progressively increases the risk level as suspicious tactics appear.

The demo uses **Gnani Timbre v3** to generate realistic synthetic voices and **Gnani Prisma v3** to transcribe each spoken turn. A local risk engine then analyzes the conversation for common scam tactics and produces an escalating risk score.

> **Important:** This project uses a fully synthetic conversation. It does not intercept real phone calls, record real users, or process real personal information.

---

## 🎯 Problem

Scam calls often manipulate victims using a combination of:

- Fake authority
- Fear and threats
- Isolation from family or friends
- Urgent money requests
- OTP or credential requests

These tactics may appear gradually rather than all at once.

Scam Shield demonstrates how a conversation can be analyzed progressively as these signals appear.

---

## 💡 How It Works

```text
Synthetic Conversation
        ↓
Gnani Timbre v3
        ↓
Synthetic Scammer / Victim Audio
        ↓
Gnani Prisma v3
        ↓
Speech-to-Text
        ↓
Local Risk Engine
        ↓
Risk Score + Scam Tactics
        ↓
Critical Warning + Voice Alert