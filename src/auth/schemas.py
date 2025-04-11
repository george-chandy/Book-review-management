from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import date
from enum import Enum

class GenderEnum(str, Enum):
    male = "male"
    female = "female"
    rather_not_say = "rather not to say"
    
class TokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class TokenData(BaseModel):
    user_id: int
    
    
class UserResponse(BaseModel):
    id: int
    first_name: str
    email: str
    phone: str
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    access_token: str
    # user: str
    user:UserResponse

class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    password: str
    gender: GenderEnum
    dob: date

class RegisterResponse(BaseModel):
    email: str
    message: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str

    model_config = ConfigDict(from_attributes=True)
    
class ResendVerificationMailRequest(BaseModel):
   email:EmailStr
  
class ResetPasswordRequest(BaseModel):
   reset_token: str
   new_password: str
  
class RefreshTokenResponse(BaseModel):
    access_token:str