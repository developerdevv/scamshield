import base64
import io
import json
import os
import time
import wave

import numpy as np
import streamlit as st

from brain import calculate_risk

st.set_page_config(page_title="Scam Shield", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    .block-container { max-width: 1200px; padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

GAP_SECONDS = 0.6  # silence between turns in the stitched call

# ---------- data ----------
with open("turns.json", "r", encoding="utf-8") as f:
    turns = json.load(f)

try:
    with open("transcripts.json", "r", encoding="utf-8") as f:
        transcripts = json.load(f)  # REAL Gnani Prisma output, made by make_transcripts.py
except FileNotFoundError:
    st.error("transcripts.json not found. Run:  python make_transcripts.py")
    st.stop()

if len(transcripts) != len(turns):
    st.error("transcripts.json and turns.json have different lengths. Re-run make_transcripts.py")
    st.stop()

if "mode" not in st.session_state:
    st.session_state.mode = "idle"
if "step" not in st.session_state:
    st.session_state.step = 0  # manual mode: index of the turn being shown


def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()


def load_clip(path):
    """Read a WAV as mono int16 samples plus its sample rate."""
    with wave.open(path) as w:
        ch, sw, rate = w.getnchannels(), w.getsampwidth(), w.getframerate()
        raw = w.readframes(w.getnframes())
    if sw != 2:
        raise ValueError(f"{path}: expected 16-bit audio, got {8 * sw}-bit")
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
    if ch > 1:
        a = a.reshape(-1, ch).mean(axis=1)
    return a, rate


@st.cache_data(show_spinner=False)
def build_full_call(n_turns, gap_seconds, _version=2):
    """Stitch t1..tN + alert into ONE wav. Returns (wav_bytes, start_offsets_seconds, total_seconds).

    start_offsets has n_turns + 1 entries: the start of each turn, then the start of the alert.
    """
    names = [f"audio/t{i + 1}.wav" for i in range(n_turns)] + ["audio/alert.wav"]
    clips = [load_clip(p) for p in names]
    rate = clips[0][1]

    pieces, offsets, pos = [], [], 0
    gap = np.zeros(int(gap_seconds * rate), dtype=np.int16)
    for a, r in clips:
        if r != rate:  # resample if one voice came back at a different rate
            x_new = np.linspace(0, len(a) - 1, int(len(a) * rate / r))
            a = np.interp(x_new, np.arange(len(a)), a)
        a = np.clip(a, -32768, 32767).astype(np.int16)
        offsets.append(pos / rate)
        pieces.append(a)
        pieces.append(gap)
        pos += len(a) + len(gap)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(np.concatenate(pieces).tobytes())
    return buf.getvalue(), offsets, pos / rate


def play_once(slot, wav_bytes):
    """Render ONE autoplaying audio player. Falls back to plain HTML on old Streamlit."""
    try:
        slot.audio(wav_bytes, format="audio/wav", autoplay=True)
    except TypeError:
        b64 = base64.b64encode(wav_bytes).decode()
        slot.markdown(
            f'<audio autoplay controls src="data:audio/wav;base64,{b64}"></audio>',
            unsafe_allow_html=True,
        )


def build_conversation(upto):
    """Conversation so far: speaker from turns.json, text from the Prisma transcript."""
    return [{"who": turns[i]["who"], "text": transcripts[i]} for i in range(upto + 1)]


def draw_transcript(slot, conversation, last_n=2):
    """Show only the latest turns so the whole page stays on one screen while recording."""
    with slot.container():
        st.subheader("📞 Call Transcript (Gnani Prisma v3.0)")
        st.caption(f"Turn {len(conversation)} of {len(turns)}")
        for m in conversation[-last_n:]:
            st.markdown("### 🔴 Scammer" if m["who"] == "scammer" else "### 🟢 Victim")
            st.write(m["text"])
            st.divider()


def draw_risk(slot, risk):
    with slot.container():
        st.subheader("🚨 Scam Risk")
        st.metric("Risk Score", f"{risk['risk_score']}%")
        level = risk["risk_level"]
        if level == "LOW":
            st.success("🟢 LOW")
        elif level == "MEDIUM":
            st.warning("🟡 MEDIUM")
        elif level == "HIGH":
            st.warning("🟠 HIGH")
        else:
            st.error("🔴 CRITICAL")
        st.progress(min(risk["risk_score"] / 100, 1.0))
        st.subheader("Detected Tactics")
        for t in risk["tactics"]:
            st.write(f"• {t}")
        if risk["warning"]:
            st.error(f"🚨 {risk['warning']}")


def sleep_until(t0, offset):
    wait = offset - (time.time() - t0)
    if wait > 0:
        time.sleep(wait)


# ---------- header ----------
st.title("🛡️ Scam Shield")
st.caption("Synthetic scam-call detection using Gnani Timbre + Prisma")
st.info(
    "A synthetic scam call is replayed turn by turn (not live call interception). "
    "Gnani Timbre generates the voices, Gnani Prisma transcribes the audio, "
    "and a rule-based risk engine tracks how the scam escalates."
)

b1, b2, b3 = st.columns(3)
auto_clicked = b1.button("▶ Auto-play full call", use_container_width=True)
manual_clicked = b2.button("⏭ Step-by-step mode", use_container_width=True)
reset_clicked = b3.button("🔄 Reset", use_container_width=True)

if reset_clicked:
    st.session_state.mode = "idle"
    st.session_state.step = 0
    st.rerun()

if manual_clicked:
    st.session_state.mode = "manual"
    st.session_state.step = 0
    st.rerun()

audio_slot = st.empty()
banner_slot = st.empty()
left, right = st.columns([2, 1])
transcript_slot = left.empty()
risk_slot = right.empty()

# ---------- AUTO-PLAY (one continuous recording, UI synced by timer) ----------
if auto_clicked:
    st.session_state.mode = "auto"
    n = len(turns)
    try:
        wav_bytes, offsets, total = build_full_call(n, GAP_SECONDS)
    except Exception as e:
        st.error(f"Could not build the call audio: {e}")
        st.stop()

    play_once(audio_slot, wav_bytes)  # starts the whole call
    t0 = time.time()

    for i in range(n):
        sleep_until(t0, offsets[i])
        conv = build_conversation(i)
        draw_transcript(transcript_slot, conv)
        draw_risk(risk_slot, calculate_risk(conv))

    sleep_until(t0, offsets[n])  # the Scam Shield voice alert starts here
    banner_slot.error("🚨 SCAM DETECTED. Hang up. Never share your OTP.")

    sleep_until(t0, total)
    st.success("✅ Call analysis complete. Scam Shield flagged the escalation before the OTP was shared.")

# ---------- STEP-BY-STEP ----------
elif st.session_state.mode == "manual":
    i = st.session_state.step
    conv = build_conversation(i)
    risk = calculate_risk(conv)
    draw_transcript(transcript_slot, conv)
    draw_risk(risk_slot, risk)

    st.divider()
    st.subheader(f"▶️ Turn {i + 1} — {turns[i]['who'].upper()}")
    st.audio(read_bytes(f"audio/t{i + 1}.wav"), format="audio/wav")

    if risk["risk_score"] >= 80:
        st.audio(read_bytes("audio/alert.wav"), format="audio/wav")

    if i + 1 >= len(turns):
        st.success("✅ Call analysis complete.")
    elif st.button(f"Continue to Turn {i + 2}", use_container_width=True):
        st.session_state.step += 1
        st.rerun()

# ---------- IDLE ----------
else:
    with transcript_slot.container():
        st.subheader("📞 Call Transcript")
        st.write("Press **Auto-play full call** to start the demo.")