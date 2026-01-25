import os
import json
import streamlit as st
from PIL import Image
from google import genai
from dotenv import load_dotenv
from typing import Union, List

# English comment: Importing our robust Pydantic model
from app.models.note import StructuredNote

load_dotenv()

class NoteProcessor:
    def __init__(self):
        """
        Initialize the processor with a secure API key lookup.
        """
        # English comment: Securely check for secrets without triggering StreamlitSecretNotFoundError
        api_key = None
        
        # 1. Try Streamlit Secrets (for Cloud Deployment)
        try:
            if "GOOGLE_API_KEY" in st.secrets:
                api_key = st.secrets["GOOGLE_API_KEY"]
        except Exception:
            # English comment: Secrets not available (standard for local run)
            pass
            
        # 2. Try Environment Variables (for Local Development via .env)
        if not api_key:
            api_key = os.getenv("GOOGLE_API_KEY")
            
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found. Please set it in Streamlit Secrets or your .env file.")
        
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.0-flash"

    def parse_note(self, source: Union[str, Image.Image]) -> List[StructuredNote]:
        """
        Extracts table rows and normalizes financial percentages using proven logic.
        """
        # English prompt: Mechanical instructions for data extraction
        prompt = (
            "Extract all rows from the table in the image. "
            "Return a JSON object with a key 'notes' which is a list of investment objects. "
            "Each object must have: issuer_bank, underlying_assets (a list of objects with ticker and name), "
            "coupon_rate_annual, and barrier_level. "
            "Process ALL rows visible in the table. "
            "IMPORTANT: If a value is 8%, return 0.08. If a value is 100%, return 1.0."
        )

        # English comment: JSON schema to guide the AI's response structure
        schema = {
            "type": "object",
            "properties": {
                "notes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "issuer_bank": {"type": "string"},
                            "underlying_assets": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "ticker": {"type": "string"},
                                        "name": {"type": "string"}
                                    },
                                    "required": ["ticker"]
                                }
                            },
                            "coupon_rate_annual": {"type": "number"},
                            "barrier_level": {"type": "number"}
                        },
                        "required": ["issuer_bank", "underlying_assets", "coupon_rate_annual", "barrier_level"]
                    }
                }
            },
            "required": ["notes"]
        }

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=[prompt, source],
            config={
                "response_mime_type": "application/json",
                "response_schema": schema,
                "temperature": 0.0,
            }
        )

        try:
            data = json.loads(response.text)
            raw_notes = data.get("notes", [])
            
            final_notes = []
            for n in raw_notes:
                # English comment: Percentage Normalization Safety Logic
                # Ensures 8.0% becomes 0.08 even if the AI outputs 8.0
                for field in ["coupon_rate_annual", "barrier_level"]:
                    val = n.get(field, 0)
                    if val > 2.0: 
                        n[field] = val / 100.0
                    # Safety check specifically for coupons
                    if n[field] > 1.0 and field == "coupon_rate_annual":
                        n[field] = n[field] / 100.0

                # English comment: Map to Pydantic model for final validation
                final_notes.append(StructuredNote(**n))
            
            return final_notes

        except Exception as e:
            # English comment: Display the raw response in UI to help debugging
            st.error(f"Critical Data Error: {e}")
            print(f"RAW AI RESPONSE: {response.text}")
            raise e