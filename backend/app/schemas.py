from pydantic import BaseModel, Field
from typing import Optional

class ShoppingRequest(BaseModel):
    request: str = Field(min_length=5, max_length=500)

class IntentUpdate(BaseModel):
    category: str = "laptop"
    max_budget: float = Field(gt=0, le=10000000)
    ram_gb: Optional[int] = None
    storage_type: Optional[str] = None
    battery_preference: Optional[str] = None

class ApprovalRequest(BaseModel):
    product_id: str
    expected_amount: float = Field(gt=0)
    currency: str = "INR"

class CaptureRequest(BaseModel):
    order_id: str
    approval_token: str
