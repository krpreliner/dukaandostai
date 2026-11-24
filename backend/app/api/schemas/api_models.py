from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class WorkerStartRequest(BaseModel):
    target_income: Optional[float] = Field(default=10000.0, description="Target monthly net income in INR")

class ApprovalActionRequest(BaseModel):
    execution_id: Optional[str] = None
    notes: Optional[str] = None

class ProductPriceUpdateRequest(BaseModel):
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None

class StandardResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
