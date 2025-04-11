from datetime import timedelta
from passlib.context import CryptContext
from fastapi import APIRouter, HTTPException, Depends, status,Request,Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from src.auth.schemas import (
    ForgotPasswordRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    ResendVerificationMailRequest,
    ResetPasswordRequest,
    RefreshTokenResponse,
    TokenType,
    User,
    UserResponse)
from src.auth.service import (
    activate_user,
    create_reset_token,
    create_user,
    create_verification_token,
    deactivate_user,
    delete_email_token,
    delete_email_tokens,
    delete_password_tokens,
    get_user_by_email,
    get_user_by_id,
    get_user_id_by_password_token,
    mark_email_verified,
    update_user_password,
    verify_the_email)
from src.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.models import EmailVerificationToken, Users
from src.auth.utils import (
    create_refresh_token,
    hash_password,
    is_password_complex,
    is_valid_email,
    is_valid_phone,
    is_valid_uuid,
    validate_and_decode_token,
    verify_password,
    create_access_token,
    get_current_user,
    send_verification_email
)
from src.auth.exceptions import (
    EmailAlreadyRegisteredException,
    EmailNotRegisteredException,
    EmailRequiredException,
    IncorrectOldPasswordException,
    InvalidEmailException,
    InvalidEmailFormatException,
    InvalidOrExpiredResetTokenException,
    InvalidOrExpiredTokenException,
    InvalidPhoneFormatException,
    JwtTokenExpiredException,
    NewPasswordRequiredException,
    PasswordRequiredException,
    InvalidCredentialsException,
    EmailNotVerifiedException,
    PasswordTooWeakException,
    PhoneRequiredException,
    FirstNameRequiredException,
    LastNameRequiredException,
    InvalidOrExpiredEmailTokenException,
    RefreshTokenRequiredException,
    ResetTokenRequiredException
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(prefix="/auth", tags=["Auth"])

@router.get("/protected-route")
async def protected_endpoint(current_user: Users = Depends(get_current_user)):
    """This route is protected. Only authenticated users can access it."""
    return {"message": f"Hello {current_user.email}, welcome to the protected route!"}

@router.post("/login")
async def login(formdata: OAuth2PasswordRequestForm = Depends() ,db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(formdata.username, db)
    
    if not formdata.username:
        raise EmailRequiredException()
    
    if not formdata.password:
        raise PasswordRequiredException()
    
    if not user.is_email_verified:
        raise EmailNotVerifiedException
    
    if not user or not verify_password(formdata.password, user.password):
        raise InvalidCredentialsException

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    
    # access_token={"access_token": access_token, "token_type": "Bearer"}
    
    response = Response()

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        path="/auth/refresh-token",
    )

    user = User.model_validate(user)
    return LoginResponse(access_token=access_token, user=user)



# @router.post("/login")
# async def login(formdata: OAuth2PasswordRequestForm = Depends() ,db: AsyncSession = Depends(get_db)):
#     user = await get_user_by_email(formdata.username, db)
    
#     if not formdata.username:
#         raise EmailRequiredException()
    
#     if not formdata.password:
#         raise PasswordRequiredException()
    
#     if not user.is_email_verified:
#         raise EmailNotVerifiedException
    
#     if not user or not verify_password(formdata.password, user.password):
#         raise InvalidCredentialsException

#     access_token = create_access_token(user.id)
#     refresh_token = create_refresh_token(user.id)
    
#     # access_token={"access_token": access_token, "token_type": "Bearer"}
    
#     response = Response()

#     response.set_cookie(
#         key="refresh_token",
#         value=refresh_token,
#         httponly=True,
#         secure=True,
#         samesite="strict",
#         path="/auth/refresh-token",
#     )

#     user = User.model_validate(user)
#     # return LoginResponse(access_token=access_token, user=user)
#     return LoginResponse(access_token=access_token, user=UserResponse)



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

@router.get("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    if not is_valid_uuid(token):
        raise InvalidOrExpiredEmailTokenException()
    
    result = await verify_the_email(token, db)  # ✅ Call the correct function

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


@router.post("/resend-verification-mail")
async def resend_verification_email(resend_request:ResendVerificationMailRequest,db:AsyncSession=Depends(get_db)):
  
    if not is_valid_email(resend_request.email):
        raise InvalidEmailException()
  
    user = await get_user_by_email(resend_request.email, db)
  
    if not user:
       raise EmailNotRegisteredException()

    if user.is_email_verified:
       raise EmailNotVerifiedException()
    
    delete_email_token(db,user.id)
    token=create_verification_token(db,user.id)
    await send_verification_email(user,token)
    return {"message": "A new verification email has been sent."}


@router.post("/reset-password")
async def reset_user_password(reset_request: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):

    if not reset_request.reset_token:
        raise ResetTokenRequiredException()

    if not reset_request.new_password:
        raise PasswordRequiredException()

    if not is_password_complex(reset_request.new_password):
        raise PasswordTooWeakException()

    user_id = await get_user_id_by_password_token(db, reset_request.reset_token)
    if not user_id:
        raise InvalidOrExpiredResetTokenException()

    hashed_password = hash_password(reset_request.new_password)
    
    await update_user_password(db, user_id, hashed_password)
    await mark_email_verified(db, user_id)
    await delete_email_tokens(db, user_id)
    await delete_password_tokens(db, user_id)
    

# @router.post("/login")
# async def login(formdata: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
#     user = await get_user_by_email(formdata.username, db)
    
#     if not user or not verify_password(formdata.password, user.password):
#         raise InvalidCredentialsException

#     access_token = create_access_token(user.id)

#     user_response = UserResponse.model_validate(user)

#     return LoginResponse(access_token=access_token, user=user_response)


@router.post("/refresh-token")
async def refresh_token(request: Request) -> RefreshTokenResponse:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise RefreshTokenRequiredException()

    try:
        token_data = validate_and_decode_token(refresh_token, TokenType.REFRESH)
    except JwtTokenExpiredException:
        raise InvalidOrExpiredTokenException()

    if not token_data:
        raise InvalidOrExpiredTokenException()

    access_token = create_access_token(token_data.user_id)
    return RefreshTokenResponse(access_token=access_token)

