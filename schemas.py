from pydantic import BaseModel
from datetime import datetime

# --- Schemas cho việc xác thực key ---

class KeyValidateRequest(BaseModel):
    licenseKey: str

class KeyValidateResponse(BaseModel):
    isValid: bool
    expiresAt: datetime | None = None
    message: str | None = None


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