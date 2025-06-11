from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# --- Schemas cho việc xác thực key ---

class KeyValidateRequest(BaseModel):
    licenseKey: str

class KeyValidateResponse(BaseModel):
    isValid: bool
    expiresAt: Optional[str] = None
    message: Optional[str] = None
    isExpired: Optional[bool] = None
    maxActivations: Optional[int] = None
    activationsUsed: Optional[int] = None
    features: List[str] = ["basic"]
    key: Optional[str] = None


# --- Schemas cho việc tạo key ---

class KeyCreateRequest(BaseModel):
    notes: str | None = None
    days_valid: int | None = None
    minutes_valid: int | None = None
    max_activations: int = 3

# Schema cơ sở cho LicenseKey, chứa các trường chung
class LicenseKeyBase(BaseModel):
    key_string: str
    expires_at: datetime
    is_active: bool
    notes: str | None = None
    activation_count: int
    max_activations: int

    class Config:
        # Giúp Pydantic tương thích với model của SQLAlchemy
        from_attributes = True

# Schema để trả về khi tạo key thành công
class LicenseKeyCreateResponse(LicenseKeyBase):
    pass


class LicenseActivationResponse(BaseModel):
    success: bool
    key: str
    expiresAt: str
    activationsUsed: int
    maxActivations: int
    features: List[str] = ["basic"] 
