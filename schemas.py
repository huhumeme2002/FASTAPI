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
    days_valid: int = 30
    notes: str | None = None

# Schema cơ sở cho LicenseKey, chứa các trường chung
class LicenseKeyBase(BaseModel):
    key_string: str
    expires_at: datetime
    is_active: bool
    notes: str | None = None

    class Config:
        # Giúp Pydantic tương thích với model của SQLAlchemy
        from_attributes = True

# Schema để trả về khi tạo key thành công
class LicenseKeyCreateResponse(LicenseKeyBase):
    pass 