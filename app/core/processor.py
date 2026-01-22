import os
from google import genai
from pydantic import ValidationError
from dotenv import load_dotenv

from app.models.note import StructuredNote

load_dotenv()

class NoteProcessor:
    """
    Handles extraction of structured data from financial documents 
    using the modern Google Gen AI SDK (Gemini 2.0+).
    """
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        # New unified client for 2026
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.0-flash" # Current stable high-speed model

    def parse_note(self, input_text: str) -> StructuredNote:
        """
        Parses raw data into a StructuredNote object using schema-driven generation.
        """
        prompt = (
            "Extract investment note parameters. "
            "Focus on: issuer, tickers, coupon rate, barrier, and dates."
        )

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=f"{prompt}\n\nInput: {input_text}",
            config={
                "response_mime_type": "application/json",
                "response_schema": StructuredNote # Direct Pydantic integration
            }
        )

        try:
            # The new SDK handles the mapping to the schema very efficiently
            return response.parsed
        except ValidationError as e:
            print(f"Schema validation failed: {e}")
            raise