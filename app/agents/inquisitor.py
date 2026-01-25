import os
from typing import List
from google import genai
from app.models.note import StructuredNote

class Inquisitor:
    """
    Agent that analyzes extracted notes and generates deep-dive questions.
    """
    def __init__(self):
        # English comment: Initialize Gemini client for analysis
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found")
            
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.0-flash"

    def generate_discovery_questions(self, notes: List[StructuredNote]) -> str:
        """
        Takes structured notes and finds risks, patterns, and contradictions.
        """
        # English comment: Prepare a clean text summary for the LLM
        context_parts = []
        for i, n in enumerate(notes, 1):
            assets = ", ".join([a.ticker for a in n.underlying_assets])
            context_parts.append(
                f"Note #{i}: Issuer={n.issuer_bank}, Assets=[{assets}], "
                f"Coupon={n.coupon_rate_annual*100}%, Barrier={n.barrier_level*100}%"
            )
        
        full_context = "\n".join(context_parts)

        # English prompt: Expert investor persona
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