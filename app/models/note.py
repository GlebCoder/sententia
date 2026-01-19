from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from .asset import Asset

class NoteCondition(BaseModel):
    """
    Defines specific trigger conditions like Autocall or Barrier levels.
    """
    level_percentage: float = Field(..., description="Level as percentage of strike (e.g., 0.6 for 60%)")
    is_active: bool = True

class StructuredNote(BaseModel):
    """
    The main model representing a bank-issued structured product.
    """
    issuer_bank: str = Field(..., description="Name of the bank that issued the note")
    underlying_assets: List[Asset] = Field(..., min_items=1)
    
    coupon_rate_annual: float = Field(..., description="Annualized coupon rate (e.g., 0.12 for 12%)")
    coupon_frequency: str = Field("Quarterly", description="Frequency of payments: Monthly, Quarterly, etc.")
    
    barrier_level: float = Field(..., description="Protection barrier level (e.g., 0.6)")
    barrier_type: str = Field("European", description="European (end of term) or American (during term)")
    
    autocall_level: Optional[float] = None
    memory_feature: bool = Field(True, description="True if missed coupons are paid later if conditions met")
    
    strike_date: Optional[date] = None
    maturity_date: Optional[date] = None
    currency: str = Field("USD", pattern="^(USD|EUR|AUD)$")

    class Config:
        # Allows creating model from dictionary/JSON easily
        populate_by_name = True