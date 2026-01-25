import sys
import os
import streamlit as st
import plotly.graph_objects as go
from PIL import Image

# English comment: Ensure the 'app' module is discoverable regardless of execution path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.core.processor import NoteProcessor
from app.agents.inquisitor import Inquisitor

# --- PAGE SETUP ---
st.set_page_config(page_title="Investment Intelligence Portal", layout="wide")

# English comment: Persistent storage for notes and conversation
if "notes" not in st.session_state:
    st.session_state.notes = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "initial_analysis" not in st.session_state:
    st.session_state.initial_analysis = (None, None)

st.title("🛡️ Investment Intelligence Portal")
st.markdown("### Advanced Structured Note Analysis & Advisory")

# --- SIDEBAR: INPUT ---
with st.sidebar:
    st.header("Data Ingestion")
    uploaded_file = st.file_uploader("Upload Document (Image)", type=['jpg', 'jpeg', 'png'])
    process_button = st.button("Run Visual Analysis 🔎")
    
    if st.button("Reset Session"):
        st.session_state.notes = None
        st.session_state.chat_history = []
        st.session_state.initial_analysis = (None, None)
        st.rerun()

    st.divider()
    st.caption("AI Engine: Model Agnostic")

# --- UI COMPONENT: RISK GAUGE ---
def create_risk_gauge(score, title):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': title, 'font': {'size': 14}},
        gauge={
            'axis': {'range': [0, 10], 'tickwidth': 1},
            'bar': {'color': "#2c3e50"},
            'steps': [
                {'range': [0, 3], 'color': "#2ecc71"},
                {'range': [3, 7], 'color': "#f1c40f"},
                {'range': [7, 10], 'color': "#e74c3c"}
            ],
        }
    ))
    fig.update_layout(height=180, margin=dict(l=20, r=20, t=30, b=10))
    return fig

# --- LOGIC: VISUAL PROCESSING ---
if uploaded_file and process_button:
    processor = NoteProcessor()
    inquisitor = Inquisitor()
    img = Image.open(uploaded_file)

    with st.status("Analyzing Document Layout...", expanded=True):
        st.session_state.notes = processor.parse_note(img)
        q_initial = inquisitor.generate_discovery_questions(st.session_state.notes)
        r_initial = inquisitor.rank_and_optimize(st.session_state.notes)
        st.session_state.initial_analysis = (q_initial, r_initial)

# --- MAIN DISPLAY AREA ---
if st.session_state.notes:
    notes = st.session_state.notes
    
    st.header("📋 Portfolio View")
    
    # English comment: Align notes in a consistent 4-column grid
    rows = [notes[i:i + 4] for i in range(0, len(notes), 4)]
    for row_notes in rows:
        cols = st.columns(4)
        for idx, note in enumerate(row_notes):
            with cols[idx]:
                # English comment: Use border containers for uniform card sizing
                with st.container(border=True):
                    st.markdown(f"#### {note.issuer_bank}")
                    st.caption(f"Assets: {', '.join([a.ticker for a in note.underlying_assets])}")
                    st.write(f"Coupon: **{note.coupon_rate_annual*100:.1f}%**")
                    st.write(f"Barrier: **{note.barrier_level*100:.1f}%**")
                    
                    # Risk Logic
                    risk_score = 3
                    if note.barrier_level > 1.0: risk_score += 4
                    if len(note.underlying_assets) > 2: risk_score += 2
                    st.plotly_chart(create_risk_gauge(risk_score, "Risk Level"), use_container_width=True)

    st.divider()

# --- DUAL PANE: ADVISOR & CHAT ---
col_report, col_chat = st.columns([1, 1])

with col_report:
    st.subheader("🏆 Strategy Report")
    if st.session_state.initial_analysis[1]:
        q_text, r_text = st.session_state.initial_analysis
        st.markdown(r_text)
        with st.expander("Show Discovery Questions"):
            st.markdown(q_text)
    else:
        st.info("Upload or paste data to generate a strategic report.")

with col_chat:
    st.subheader("💬 Advisor Chat")
    
    # English comment: Render historical messages
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # English comment: Input for both questions and text-based note ingestion
    if prompt := st.chat_input("Ask a question or paste note details here..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            inquisitor = Inquisitor()
            
            # Logic: If no notes exist, treat input as data ingestion. Else, follow-up.
            if st.session_state.notes is None:
                with st.spinner("Analyzing text for financial data..."):
                    # Process text input
                    response = inquisitor.client.models.generate_content(
                        model=inquisitor.model_id,
                        contents=f"The user has provided text instead of an image. "
                                 f"First, extract structured note details (Issuer, Assets, Coupon, Barrier). "
                                 f"Second, provide a risk analysis. Text: {prompt}"
                    )
            else:
                with st.spinner("Thinking..."):
                    # Process follow-up question
                    response = inquisitor.client.models.generate_content(
                        model=inquisitor.model_id,
                        contents=f"Context: {st.session_state.notes}\nUser Question: {prompt}\n"
                                 f"Respond as a senior advisor. Be concise."
                    )
            
            st.markdown(response.text)
            st.session_state.chat_history.append({"role": "assistant", "content": response.text})

if not st.session_state.notes and not st.session_state.chat_history:
    st.info("👈 Use the sidebar to upload an image, or paste note details into the chat to begin.")