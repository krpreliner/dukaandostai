from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional

class WorkerStartRequest(BaseModel):
    target_income: Optional[float] = Field(
        default=10000.0,
        gt=0,
        le=100000.0,
        description="Target monthly net income in INR (must be positive)"
    )

class ApprovalActionRequest(BaseModel):
    execution_id: Optional[str] = None
    notes: Optional[str] = Field(default=None, max_length=500)

class ProductPriceUpdateRequest(BaseModel):
    cost_price: Optional[float] = Field(default=None, gt=0, description="Cost price must be positive")
    selling_price: Optional[float] = Field(default=None, gt=0, description="Selling price must be positive")

class StandardResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
