import os
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

import crud, models, schemas
from database import SessionLocal, engine, Base

# Tạo tất cả các bảng trong database (chỉ chạy khi chưa có bảng)
# Trong môi trường sản xuất, bạn có thể muốn dùng Alembic để quản lý migrations
Base.metadata.create_all(bind=engine)

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
        return {"isValid": False, "message": "Key bản quyền không tồn tại hoặc đã bị vô hiệu hóa."}

    if key_record.expires_at < datetime.utcnow():
        return {"isValid": False, "message": "Key bản quyền đã hết hạn."}

    return {"isValid": True, "expiresAt": key_record.expires_at}


@app.post("/api/generate-key", response_model=schemas.LicenseKeyCreateResponse, tags=["Admin"], dependencies=[Depends(verify_admin)])
def generate_new_key(request: schemas.KeyCreateRequest, db: Session = Depends(get_db)):
    """
    Tạo một key bản quyền mới. Yêu cầu có header `X-Admin-Secret`.
    """
    new_key = crud.create_license_key(db, key_data=request)
    return new_key 