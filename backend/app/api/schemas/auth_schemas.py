from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, description="Password must be at least 8 characters")
    full_name: str = Field(min_length=2, max_length=100)
    store_name: Optional[str] = Field(default="My Kirana Store", max_length=150)
    store_location: Optional[str] = Field(default="Ranchi, Jharkhand", max_length=100)

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class StoreInfo(BaseModel):
    store_id: str
    name: str
    location: str
    owner_name: str
    role: str
    initial_net_income: float
    target_net_income: float
    current_net_income: float
    simulated_net_income: float

class UserInfo(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    user: UserInfo
    stores: List[StoreInfo]

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class StoreCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    location: Optional[str] = Field(default="Ranchi, Jharkhand", max_length=100)

class AddMemberRequest(BaseModel):
    email: EmailStr
    role: str = Field(default="STAFF", pattern="^(OWNER|MANAGER|STAFF|VIEWER)$")
