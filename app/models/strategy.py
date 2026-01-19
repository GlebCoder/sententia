from pydantic import BaseModel, Field
from typing import List

class InvestorProfile(BaseModel):
    """
    Captures user's risk tolerance and investment goals.
    """
    risk_appetite: str = Field(..., description="Options: Conservative, Moderate, Aggressive")
    target_annual_return: float = Field(..., description="Expected yield in decimals")
    min_acceptable_barrier: float = Field(0.6, description="Lowest protection level user is willing to accept")
    excluded_sectors: List[str] = []
    preferred_markets: List[str] = ["US", "EU", "AU"]