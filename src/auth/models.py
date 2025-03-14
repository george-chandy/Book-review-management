from sqlalchemy.dialects.postgresql import ENUM
from src.models import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship

gender_enum = ENUM("male", "female", "other", name="gender_enum", create_type=True)

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    dob = Column(DateTime, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    is_email_verified = Column(Boolean, nullable=True)
    is_active = Column(Boolean, default=True)
    deactivated_at = Column(DateTime, nullable=True)

    verification_token = relationship(
        "EmailVerificationToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )

class EmailVerificationToken(Base):
    __tablename__ = "email_verification_token"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE")) 
    token = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship("Users", back_populates="verification_token")

class PasswordResetToken(Base) :
    __tablename__ = "password_reset_token"
    
    id = Column(Integer,primary_key=True,autoincrement=True)
    user_id = Column(Integer,ForeignKey("users.id"),unique=True)
    token = Column(String(255),unique=True,nullable=False)
    created_at = Column(DateTime(timezone=True),nullable=False)
    expires_at = Column(DateTime(timezone=True),nullable=False)