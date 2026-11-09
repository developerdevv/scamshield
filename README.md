# 🛡️ Scam Shield

AI-powered synthetic scam-call detection using Gnani AI's Timbre and Prisma APIs.

## 🎯 Problem

Scam calls often use:

- Fake authority
- Fear and threats
- Isolation from family
- Money requests
- OTP/credential requests

Scam Shield demonstrates how these patterns can be detected progressively during a synthetic scam conversation.

## 💡 How It Works

```text
Synthetic Conversation
        ↓
Gnani Timbre v3
        ↓
Synthetic Voice Audio
        ↓
Gnani Prisma v3
        ↓
Speech-to-Text
        ↓
Local Risk Engine
        ↓
Risk Score + Scam Tactics
        ↓
Critical Warning