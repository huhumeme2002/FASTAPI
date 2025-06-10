from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
import string

import models
import schemas

def get_key_by_string(db: Session, key_string: str):
    """
    Tìm một key trong database bằng chuỗi key.
    """
    return db.query(models.LicenseKey).filter(models.LicenseKey.key_string == key_string).first()

def generate_license_key(length=24, parts=4, prefix="PRO"):
    """
    Tạo một chuỗi key ngẫu nhiên và an toàn.
    Ví dụ: PRO-ABCDE-FGHIJ-KLMNO-PQRST
    """
    alphabet = string.ascii_uppercase + string.digits
    segment_length = length // parts
    key_segments = []
    
    for _ in range(parts):
        segment = ''.join(secrets.choice(alphabet) for _ in range(segment_length))
        key_segments.append(segment)
        
    return f"{prefix}-{'-'.join(key_segments)}"


def create_license_key(db: Session, key_data: schemas.KeyCreateRequest):
    """
    Tạo một record key mới trong database.
    """
    # Ưu tiên tạo key theo phút nếu được cung cấp
    if key_data.minutes_valid:
        expires_at = datetime.utcnow() + timedelta(minutes=key_data.minutes_valid)
    # Nếu không, dùng ngày (mặc định là 30 ngày nếu không cung cấp cả hai)
    else:
        days = key_data.days_valid if key_data.days_valid is not None else 30
        expires_at = datetime.utcnow() + timedelta(days=days)

    # Tạo key string duy nhất
    new_key_string = generate_license_key()
    while get_key_by_string(db, new_key_string):
        new_key_string = generate_license_key()

    db_key = models.LicenseKey(
        key_string=new_key_string,
        expires_at=expires_at,
        notes=key_data.notes,
        max_activations=key_data.max_activations
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    return db_key 