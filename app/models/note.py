from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

class Asset(BaseModel):
    # English comment: Allow multiple names for the same field to prevent mapping errors
    ticker: str = Field(..., alias="symbol")
    name: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)

class StructuredNote(BaseModel):
    issuer_bank: str = Field(..., alias="issuer")
    
    # English comment: This is the most common failure point. 
    # We allow the AI to be slightly off in its naming.
    underlying_assets: List[Asset] = Field(..., alias="assets")
    
    coupon_rate_annual: float = Field(..., alias="coupon")
    barrier_level: float = Field(..., alias="barrier")
    currency: Optional[str] = "USD"

    model_config = ConfigDict(populate_by_name=True)