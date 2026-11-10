import re


def calculate_risk(conversation):
    text = " ".join(
        message["text"].lower()
        for message in conversation
    )

    score = 0
    tactics = []

    # Fake authority
    if re.search(r"\bcbi\b|\bpolice\b|\binspector\b|\bofficer\b|सीबीआई|सीबीआइ|इंस्पेक्टर|इन्स्पेक्टर|पुलिस", text):
        score += 20
        tactics.append("fake authority")

    # Fear / threat
    if re.search(
        r"drugs|ड्रग्स|arrest|अरेस्ट|गिरफ्तार|case|केस|digital arrest|डिजिटल अरेस्ट",
        text
    ):
        score += 20
        tactics.append("fear/threat")

    # Isolation
    if re.search(
        r"किसी को.*मत|घर वालों.*नहीं|फोन मत करना|don't tell|not tell",
        text
    ):
        score += 20
        tactics.append("isolation")

    # Money
    if re.search(
        r"पैसे|रुपये|₹|50,000|हज़ार|हजार|भेजिए|send money",
        text
    ):
        score += 20
        tactics.append("money request")

    # OTP / credentials
    if re.search(
        r"otp|ओटीपी|password|पासवर्ड|pin|पिन",
        text
    ):
        score += 25
        tactics.append("OTP/credential request")

    # Escalation bonus
    if "isolation" in tactics and (
        "money request" in tactics
        or "OTP/credential request" in tactics
    ):
        score += 10

    score = min(score, 100)

    if score < 30:
        level = "LOW"
    elif score < 60:
        level = "MEDIUM"
    elif score < 80:
        level = "HIGH"
    else:
        level = "CRITICAL"

    # Only warn at critical risk
    if score >= 80:
        warning = "OTP bilkul mat dijiye. Call kaat dijiye."
    else:
        warning = ""

    return {
        "risk_score": score,
        "risk_level": level,
        "tactics": tactics,
        "warning": warning
    }