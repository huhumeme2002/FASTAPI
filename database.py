import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Tải các biến môi trường từ file .env (chủ yếu cho local dev)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("Biến môi trường DATABASE_URL chưa được thiết lập.")

# create_engine là điểm khởi đầu của SQLAlchemy
# connect_args chỉ cần thiết cho SQLite, không cần cho PostgreSQL trên Render
engine = create_engine(DATABASE_URL)

# Mỗi instance của SessionLocal sẽ là một session kết nối với DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class để các model kế thừa
Base = declarative_base() 