import os
import streamlit as st
from typing import List
from google import genai
from dotenv import load_dotenv

# English comment: Importing our shared financial data model
from app.models.note import StructuredNote

# English comment: Load local .env for development
load_dotenv()

class Inquisitor:
    """
    Agent that analyzes extracted notes and generates deep-dive questions.
    Updated with secure key handling for seamless deployment.
    """
    def __init__(self):
        # English comment: Securely check for secrets without triggering StreamlitSecretNotFoundError
        api_key = None
        
        # 1. Try Streamlit Secrets (for Cloud Deployment)
        try:
            if "GOOGLE_API_KEY" in st.secrets:
                api_key = st.secrets["GOOGLE_API_KEY"]
        except Exception:
            # English comment: Secrets not accessible (normal for local environment)
            pass
            
        # 2. Try Environment Variables (for Local Development)
        if not api_key:
            api_key = os.getenv("GOOGLE_API_KEY")
            
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found. Please set it in Secrets or .env file.")
            
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.0-flash"

    def generate_discovery_questions(self, notes: List[StructuredNote]) -> str:
        """
        Takes structured notes and finds risks, patterns, and contradictions.
        """
        # English comment: Format extracted notes into a clear context for the AI
        context_parts = []
        for i, n in enumerate(notes, 1):
            assets = ", ".join([a.ticker for a in n.underlying_assets])
            context_parts.append(
                f"Note #{i}: Issuer={n.issuer_bank}, Assets=[{assets}], "
                f"Coupon={n.coupon_rate_annual*100:.1f}%, Barrier={n.barrier_level*100:.1f}%"
            )
        
        full_context = "\n".join(context_parts)

        # English prompt: Expert investor persona with critical analysis instructions
        prompt = (
            "You are a Senior Investment Strategist. Your goal is to 'interrogate' these financial products. "
            "Below is a list of structured notes extracted from a client's document:\n\n"
            f"{full_context}\n\n"
            "TASK:\n"
            "1. Identify the 'Worst-of' risk (which assets are most volatile).\n"
            "2. Compare the Barrier Levels (flag notes with 125% barrier as high risk).\n"
            "3. Look for concentration (e.g., multiple notes on the same assets).\n"
            "4. Generate 3 sharp, professional 'Discovery Questions' for the investor to test their understanding.\n\n"
            "Return the questions in English as a numbered list. Be concise and critical."
        )

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )

        return response.text
    
    def rank_and_optimize(self, notes: List[StructuredNote]) -> str:
        """
        Ranks notes from best to worst and suggests ticker improvements based on risk-reward.
        """
        context = "\n".join([
            f"- {n.issuer_bank}: Assets={[a.ticker for a in n.underlying_assets]}, "
            f"Coupon={n.coupon_rate_annual*100:.1f}%, Barrier={n.barrier_level*100:.1f}%"
            for n in notes
        ])

        prompt = (
            "You are a Senior Portfolio Manager. Analyze these structured notes:\n"
            f"{context}\n\n"
            "TASK:\n"
            "1. RANKING: List the notes from 'Best Risk-Reward' to 'Worst'. Explain why.\n"
            "2. CRITIQUE: For the worst notes, explain why they are dangerous (specifically the 125% barrier issue).\n"
            "3. OPTIMIZATION: Suggest 2-3 specific ticker changes. "
            "For example, replace highly volatile assets with more stable blue-chip stocks (e.g., MSFT, XOM) or safer ETFs.\n"
            "4. VERDICT: Give a final recommendation on which one to buy, if any.\n\n"
            "Format the output clearly using Markdown for the ranking list and verdict."
        )

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )
        return response.text