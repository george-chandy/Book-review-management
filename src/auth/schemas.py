from pydantic import BaseModel, EmailStr
from datetime import date
from enum import Enum

class GenderEnum(str, Enum):
    male = "male"
    female = "female"
    rather_not_say = "rather not to say"

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
    # message: str