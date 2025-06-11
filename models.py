from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class LicenseKey(Base):
    __tablename__ = "license_keys"

    id = Column(Integer, primary_key=True, index=True)
    key_string = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    notes = Column(String, nullable=True)
    activation_count = Column(Integer, default=0)
    max_activations = Column(Integer, default=3)
    activation_logs = relationship("ActivationLog", back_populates="key")


class ActivationLog(Base):
    __tablename__ = "activation_logs"

    id = Column(Integer, primary_key=True, index=True)
    key_id = Column(Integer, ForeignKey("license_keys.id"))
    key = relationship("LicenseKey", back_populates="activation_logs")
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow) 
