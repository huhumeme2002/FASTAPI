import os
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status, Header, Request
from sqlalchemy.orm import Session

import crud, models, schemas
from database import SessionLocal, engine, Base

# --- XÓA VÀ TẠO LẠI BẢNG KHI KHỞI ĐỘNG (DÀNH CHO MÔI TRƯỜNG TEST) ---
# CẢNH BÁO: Thao tác này sẽ xóa toàn bộ dữ liệu trong các bảng mỗi khi deploy.
# Chỉ dùng để đảm bảo schema được cập nhật.
print("Dropping and recreating tables...")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("Tables recreated successfully.")
# --- KẾT THÚC KHỐI MÃ TEST ---

app = FastAPI(
    title="License Key API",
    description="API để quản lý và xác thực key bản quyền.",
    version="1.0.0"
)

# Dependency để lấy DB session cho mỗi request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency để xác thực admin
def verify_admin(x_admin_secret: str = Header(...)):
    admin_secret_key = os.getenv("ADMIN_SECRET_KEY")
    if not admin_secret_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ADMIN_SECRET_KEY chưa được cấu hình trên server."
        )
    if x_admin_secret != admin_secret_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sai mật khẩu admin."
        )

@app.get("/", tags=["Status"])
def read_root():
    """Endpoint để kiểm tra server có đang hoạt động không."""
    return {"status": "ok", "message": "Welcome to the License Key API!"}


@app.post("/api/validate-key", response_model=schemas.KeyValidateResponse, tags=["License Validation"])
def validate_key(request: schemas.KeyValidateRequest, db: Session = Depends(get_db)):
    """
    Xác thực một key bản quyền. Đây là endpoint chính cho extension của bạn.
    """
    key_record = crud.get_key_by_string(db, key_string=request.licenseKey)

    if not key_record or not key_record.is_active:
        return {
            "isValid": False, 
            "message": "Key bản quyền không tồn tại hoặc đã bị vô hiệu hóa."
        }

    is_expired = key_record.expires_at < datetime.utcnow()
    if is_expired:
        return {
            "isValid": False, 
            "message": "Key bản quyền đã hết hạn.",
            "isExpired": True
        }

    max_activations_reached = key_record.activation_count >= key_record.max_activations
    if max_activations_reached:
        return {
            "isValid": False, 
            "message": f"Key đã đạt giới hạn kích hoạt tối đa ({key_record.max_activations} lần).",
            "maxActivationsReached": True
        }

    return {
        "isValid": True,
        "expiresAt": key_record.expires_at.isoformat(),
        "key": key_record.key_string,
        "features": ["basic"],
        "maxActivations": key_record.max_activations,
        "activationsUsed": key_record.activation_count
    }


@app.post("/api/activate", response_model=schemas.LicenseActivationResponse, tags=["License Activation"])
def activate_license(request: Request, key_request: schemas.KeyValidateRequest, db: Session = Depends(get_db)):
    """
    Kích hoạt key cho một thiết bị cụ thể.
    """
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    key_record = crud.get_key_by_string(db, key_string=key_request.licenseKey)
    
    if not key_record or not key_record.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Key bản quyền không tồn tại hoặc đã bị vô hiệu hóa."
        )
    
    if key_record.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Key bản quyền đã hết hạn."
        )
    
    if key_record.activation_count >= key_record.max_activations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Key đã đạt giới hạn kích hoạt tối đa ({key_record.max_activations} lần)."
        )
    
    # Tăng số lần kích hoạt
    key_record.activation_count += 1
    
    # Tạo bản ghi kích hoạt
    db_activation = models.ActivationLog(
        key_id=key_record.id,
        ip_address=client_ip,
        user_agent=user_agent
    )
    db.add(db_activation)
    
    db.commit()
    db.refresh(key_record)
    
    return {
        "success": True,
        "key": key_record.key_string,
        "expiresAt": key_record.expires_at.isoformat(),
        "activationsUsed": key_record.activation_count,
        "maxActivations": key_record.max_activations,
        "features": ["basic"]
    }


@app.post("/api/generate-key", response_model=schemas.LicenseKeyCreateResponse, tags=["Admin"], dependencies=[Depends(verify_admin)])
def generate_new_key(request: schemas.KeyCreateRequest, db: Session = Depends(get_db)):
    """
    Tạo một key bản quyền mới. Yêu cầu có header `X-Admin-Secret`.
    """
    new_key = crud.create_license_key(db, key_data=request)
    return new_key 
