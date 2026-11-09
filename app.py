import streamlit as st
import json
from brain import calculate_risk


st.markdown("""
<style>
    .main {
        background-color: #0f172a;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
    }

    .risk-card {
        padding: 20px;
        border-radius: 15px;
        background: #1e293b;
        border: 1px solid #334155;
        margin-bottom: 20px;
    }

    .scammer {
        background: #3f1d1d;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
    }

    .victim {
        background: #172d22;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
    }

    .critical {
        background: #450a0a;
        border: 2px solid #ef4444;
        padding: 20px;
        border-radius: 15px;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)


st.set_page_config(
    page_title="Scam Shield",
    page_icon="🛡️",
    layout="wide"
)

# Load turns
with open("turns.json", "r", encoding="utf-8") as f:
    turns = json.load(f)

# Session state
if "current_turn" not in st.session_state:
    st.session_state.current_turn = 0

if "conversation" not in st.session_state:
    st.session_state.conversation = []


# Restart
if st.button("🔄 Restart Demo"):
    st.session_state.current_turn = 0
    st.session_state.conversation = []
    st.rerun()


# Current turn
if st.session_state.current_turn < len(turns):

    turn = turns[st.session_state.current_turn]

    if len(st.session_state.conversation) <= st.session_state.current_turn:
        st.session_state.conversation.append({
            "who": turn["who"],
            "text": turn["text"]
        })

else:
    turn = None


# Calculate risk
risk = calculate_risk(st.session_state.conversation)


# Header
st.title("🛡️ Scam Shield")
st.caption("Synthetic scam-call detection using Gnani Timbre + Prisma")

st.info(
    "A synthetic scam call is replayed turn-by-turn. "
    "Timbre generates the voices, Prisma transcribes the speech, "
    "and Scam Shield analyzes the conversation for scam tactics."
)


# Main layout
left, right = st.columns([2, 1])


# Conversation
with left:

    st.subheader("📞 Call Transcript")

    for message in st.session_state.conversation:

        if message["who"] == "scammer":
            st.markdown("### 🔴 Scammer")
        else:
            st.markdown("### 🟢 Victim")

        st.write(message["text"])
        st.divider()


# Risk panel
with right:

    st.subheader("🚨 Scam Risk")

    st.metric(
        "Risk Score",
        f"{risk['risk_score']}%"
    )

    if risk["risk_level"] == "LOW":
        st.success("🟢 LOW")

    elif risk["risk_level"] == "MEDIUM":
        st.warning("🟡 MEDIUM")

    elif risk["risk_level"] == "HIGH":
        st.warning("🟠 HIGH")

    else:
        st.error("🔴 CRITICAL")

    st.progress(risk["risk_score"] / 100)

    st.subheader("Detected Tactics")

    for tactic in risk["tactics"]:
        st.write(f"• {tactic}")

    if risk["warning"]:
        st.error(f"🚨 {risk['warning']}")

    if risk["risk_score"] >= 80:
        try:
            with open("audio/alert.wav", "rb") as alert_file:
                alert_audio = alert_file.read()

            st.audio(
                alert_audio,
                format="audio/wav"
            )

        except FileNotFoundError:
            st.warning("Alert audio not found.")


# Audio + next turn
st.divider()

if turn:

    turn_number = st.session_state.current_turn + 1

    audio_path = f"audio/t{turn_number}.wav"

    st.subheader(
        f"▶️ Turn {turn_number} — {turn['who'].upper()}"
    )

    # Play generated Timbre audio
    try:
        with open(audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()

        st.audio(
            audio_bytes,
            format="audio/wav"
        )

    except FileNotFoundError:
        st.warning("Audio file not found.")

    if st.button(
        f"Continue to Turn {turn_number + 1}"
        if turn_number < len(turns)
        else "Finish Call",
        use_container_width=True
    ):
        st.session_state.current_turn += 1
        st.rerun()

else:

    st.success(
        "✅ Call analysis complete. Scam Shield detected the scam escalation."
    )

    if st.button("🔄 Run Demo Again", use_container_width=True):
        st.session_state.current_turn = 0
        st.session_state.conversation = []
        st.rerun()