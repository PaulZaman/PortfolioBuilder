from pydantic import BaseModel, EmailStr
from pydantic import BaseModel, Field
from typing import List
from datetime import date

class Portfolio(BaseModel):
    tickers: List[str]
    weights: List[float]
    start_date: date
    name: str = "New Portfolio"  # Optional, with default value
