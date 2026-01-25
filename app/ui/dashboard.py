import sys
import os
import streamlit as st
import plotly.graph_objects as go
from PIL import Image

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.core.processor import NoteProcessor
from app.agents.inquisitor import Inquisitor

st.set_page_config(page_title="Investment Intelligence Portal", layout="wide")

# Initialize Session State for Chat and Data
if "notes" not in st.session_state:
    st.session_state.notes = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("🛡️ Investment Intelligence Portal")
st.markdown("### Structural Note Analysis & Advisory")

# --- SIDEBAR: DATA INPUT ---
with st.sidebar:
    st.header("Data Ingestion")
    uploaded_file = st.file_uploader("Upload Note Image", type=['jpg', 'jpeg', 'png'])
    process_button = st.button("Analyze Document 🔎")
    
    if st.button("Clear Session"):
        st.session_state.notes = None
        st.session_state.chat_history = []
        st.rerun()

    st.divider()
    st.caption("AI-Powered Financial Analysis Engine")

def create_risk_gauge(score, title):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': title, 'font': {'size': 16}},
        gauge={
            'axis': {'range': [0, 10]},
            'bar': {'color': "black"},
            'steps': [
                {'range': [0, 3], 'color': "#2ecc71"},
                {'range': [3, 7], 'color': "#f1c40f"},
                {'range': [7, 10], 'color': "#e74c3c"}
            ],
        }
    ))
    fig.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
    return fig

# --- MAIN LOGIC: PROCESSING ---
if uploaded_file and process_button:
    processor = NoteProcessor()
    inquisitor = Inquisitor()
    img = Image.open(uploaded_file)

    with st.status("Interrogating Assets...", expanded=True):
        st.session_state.notes = processor.parse_note(img)
        # Store initial analysis in history
        q_initial = inquisitor.generate_discovery_questions(st.session_state.notes)
        r_initial = inquisitor.rank_and_optimize(st.session_state.notes)
        st.session_state.initial_analysis = (q_initial, r_initial)

# --- DISPLAY SECTION ---
if st.session_state.notes:
    notes = st.session_state.notes
    
    st.header("📋 Portfolio Overview")
    
    # Dynamic Grid Alignment: Max 4 notes per row
    rows = [notes[i:i + 4] for i in range(0, len(notes), 4)]
    for row_notes in rows:
        cols = st.columns(4) # Always create 4 columns for alignment
        for idx, note in enumerate(row_notes):
            with cols[idx]:
                with st.container(border=True):
                    st.markdown(f"**{note.issuer_bank}**")
                    st.caption(f"Assets: {', '.join([a.ticker for a in note.underlying_assets])}")
                    st.write(f"Coupon: **{note.coupon_rate_annual*100:.1f}%**")
                    st.write(f"Barrier: **{note.barrier_level*100:.1f}%**")
                    
                    risk_score = 3
                    if note.barrier_level > 1.0: risk_score += 4
                    if len(note.underlying_assets) > 2: risk_score += 2
                    st.plotly_chart(create_risk_gauge(risk_score, ""), use_container_width=True)

    st.divider()

    # --- CHAT & ANALYSIS INTERFACE ---
    col_chat, col_report = st.columns([1, 1])

    with col_report:
        st.subheader("🏆 Strategic Verdict")
        q_text, r_text = st.session_state.initial_analysis
        st.markdown(r_text)
        with st.expander("View Discovery Questions"):
            st.markdown(q_text)

    with col_chat:
        st.subheader("💬 Interactive Advisor")
        
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask a follow-up question about these notes..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # English comment: Use Inquisitor for follow-up logic
            with st.chat_message("assistant"):
                # Simplified follow-up call (can be expanded in Inquisitor class later)
                inquisitor = Inquisitor()
                # We pass the prompt + note context
                response = inquisitor.client.models.generate_content(
                    model=inquisitor.model_id,
                    contents=f"Context: {st.session_state.notes}\nUser Question: {prompt}\nAnswer as a senior advisor."
                )
                st.markdown(response.text)
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})

else:
    st.info("👈 Upload an investment document to begin analysis.")