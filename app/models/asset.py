from pydantic import BaseModel, Field
from typing import Optional

class Asset(BaseModel):
    """
    Represents a financial instrument (stock, ETF, index) 
    within a structured product.
    """
    ticker: str = Field(..., example="AAPL")
    name: Optional[str] = Field(None, description="Full company name")
    sector: Optional[str] = Field(None, description="Industry sector")
    is_benchmark: bool = Field(False, description="True if asset is a benchmark like SPX")

    class Config:
        frozen = True # Makes the asset immutable