from datetime import timedelta
from passlib.context import CryptContext
from fastapi import APIRouter, HTTPException, Depends, status, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from src.auth.schemas import (
    ForgotPasswordRequest,
    RegisterRequest,
    RegisterResponse,
    User)
from src.auth.service import (
    activate_user,
    create_reset_token,
    create_user,
    create_verification_token,
    deactivate_user,
    get_user_by_email,
    verify_email)
from src.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.models import EmailVerificationToken, Users
from src.auth.utils import (
    is_password_complex,
    is_valid_email,
    is_valid_phone,
    is_valid_uuid,
    verify_password,
    create_access_token,
    get_current_user
)
from src.auth.exceptions import (
    EmailAlreadyRegisteredException,
    EmailNotRegisteredException,
    EmailRequiredException,
    IncorrectOldPasswordException,
    InvalidEmailFormatException,
    InvalidPhoneFormatException,
    NewPasswordRequiredException,
    PasswordRequiredException,
    InvalidCredentialsException,
    EmailNotVerifiedException,
    PasswordTooWeakException,
    PhoneRequiredException,
    FirstNameRequiredException,
    LastNameRequiredException,
    InvalidOrExpiredEmailTokenException
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(prefix="/auth", tags=["Auth"])

@router.get("/protected-route")
async def protected_endpoint(current_user: Users = Depends(get_current_user)):
    """This route is protected. Only authenticated users can access it."""
    return {"message": f"Hello {current_user.email}, welcome to the protected route!"}

@router.post("/login")
async def login(formdata: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(formdata.username, db)
    
    if not formdata.username:
        raise EmailRequiredException()
    
    if not formdata.password:
        raise PasswordRequiredException()
    
    if not user.is_email_verified:
        raise EmailNotVerifiedException
    
    if not user or not verify_password(formdata.password, user.password):
        raise InvalidCredentialsException

    access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=30))

    return {"access_token": access_token, "token_type": "Bearer"}

@router.post("/register", response_model=RegisterResponse)
async def register_user(
    user_data: RegisterRequest, 
    db: AsyncSession = Depends(get_db)
):
    if user_data.first_name is None:
        raise FirstNameRequiredException()
    
    if user_data.last_name is None:
        raise LastNameRequiredException()
    
    if user_data.email is None:
        raise EmailRequiredException()
    
    if user_data.phone is None:
        raise PhoneRequiredException()
    
    if user_data.password is None:  
        raise PasswordRequiredException()
    
    if not user_data.email.count("@") == 1 or not user_data.email.count(".") > 0:
        raise InvalidEmailFormatException()
    
    if not is_password_complex(user_data.password):
        raise PasswordTooWeakException()
    
    if not is_valid_email(user_data.email):
        raise InvalidEmailFormatException()
    
    if not is_valid_phone(user_data.phone):
        raise InvalidPhoneFormatException()

    if await get_user_by_email(user_data.email, db):
        raise EmailAlreadyRegisteredException()
    
    user = await create_user(user_data, db)
    # user = User.model_validate(user)
    user = User.model_validate(user.__dict__)
    return RegisterResponse(email=user_data.email, message="verify mail id")

@router.get("/verify-email", status_code=status.HTTP_204_NO_CONTENT)
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    if not is_valid_uuid(token):
        raise InvalidOrExpiredEmailTokenException()
    
    result = await verify_email(token, db)

    return result

@router.patch("/deactivate-account")
async def deactivate_account(current_user: Users = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    
    user = await get_user_by_email(current_user.email, db)

    if user is None:
        raise EmailNotRegisteredException()
    
    if not user.is_active:
        await activate_user(current_user, db)
        return {"message": "account activated successfully"}
    if user.is_active:
        await deactivate_user(current_user, db)
        return{"message":"account activated successfully"}
        
@router.post("/forgot-password", status_code=status.HTTP_204_NO_CONTENT)
async def forgot_password(request: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    
    if not request.email:
        raise EmailRequiredException()
    
    if not is_valid_email(request.email):
        raise InvalidEmailFormatException()
    
    user = get_user_by_email(db, request.email)
    
    if not user:
        raise EmailNotRegisteredException()

    await create_reset_token(request.email, db)

@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(old_password:str, new_password:str, current_user: Users = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(current_user.email, db)
    
    if not verify_password(old_password, user.password):
        raise IncorrectOldPasswordException()
    
    if not new_password:
        raise NewPasswordRequiredException()
    
    if not old_password:
        raise PasswordRequiredException()
    
    hashed_password = pwd_context.hash(new_password)
    user.password = hashed_password
    await db.commit()
    return {"message": "password changed successfully"}