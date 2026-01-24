import os
import json
from PIL import Image
from google import genai
from dotenv import load_dotenv
from typing import Union, List

# English comment: Importing our robust Pydantic model
from app.models.note import StructuredNote

# Load environment variables
load_dotenv()

class NoteProcessor:
    """
    Core engine for extracting structured financial data from documents.
    Uses a manual schema and normalization logic to ensure data accuracy.
    """
    def __init__(self):
        # English comment: Securely fetch API key from environment
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.0-flash"

    def parse_note(self, source: Union[str, Image.Image]) -> List[StructuredNote]:
        """
        Extracts every row from a table and normalizes financial percentages.
        """
        # English prompt: Strict mechanical instructions
        prompt = (
            "Extract all rows from the table in the image. "
            "Return a JSON object with a key 'notes' which is a list of investment objects. "
            "Each object must have: issuer_bank, underlying_assets (a list of objects with ticker and name), "
            "coupon_rate_annual, and barrier_level. "
            "Process ALL rows visible in the table. "
            "IMPORTANT: If a value is 8%, return 0.08. If a value is 100%, return 1.0."
        )

        # English comment: Manual schema definition to prevent Pydantic/Gemini naming conflicts
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
                # English comment: Percentage Normalization Logic
                # Prevents 8.0% from becoming 8.0 or 800.0
                for field in ["coupon_rate_annual", "barrier_level"]:
                    val = n.get(field, 0)
                    if val > 2.0: # If value is e.g. 8.0 or 100.0
                        n[field] = val / 100.0
                    if n[field] > 1.0 and field == "coupon_rate_annual":
                        # Safety check: coupons are rarely > 100%
                        n[field] = n[field] / 100.0

                # English comment: Map to Pydantic model for final validation
                final_notes.append(StructuredNote(**n))
            
            return final_notes

        except Exception as e:
            # English comment: Log the raw response if parsing fails
            print(f"CRITICAL DATA ERROR: {response.text}")
            raise e