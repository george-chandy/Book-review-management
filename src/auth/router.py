from datetime import timedelta
from sqlalchemy.future import select
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from src.auth.schemas import RegisterRequest, RegisterResponse
from src.auth.service import (
    activate_user,
    create_user,
    deactivate_user,
    get_user_by_email)
from src.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.models import Users
from src.auth.utils import (
    verify_password,
    create_access_token,
    get_current_user
)

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.get("/protected-route")
async def protected_endpoint(current_user: Users = Depends(get_current_user)):
    """This route is protected. Only authenticated users can access it."""
    return {"message": f"Hello {current_user.email}, welcome to the protected route!"}

@router.post("/register", response_model=RegisterResponse)
async def register_user(user_data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user_by_email(user_data.email, db)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = await create_user(user_data, db)  # ✅ Ensure `await` is used here
    return user



# @router.post("/login")
# async def login(formdata: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
#     stmt = select(Users).where(Users.email == formdata.username)
#     result = await db.execute(stmt)
#     user = result.scalars().first()

#     if not user or not verify_password(formdata.password, user.password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )

#     access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=30))
#     return {"access_token": access_token, "token_type": "Bearer"}


@router.post("/login")
async def login(formdata: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    exec = select(Users).where(Users.email == formdata.username)
    result = await db.execute(exec)
    user = result.scalars().first()

    if not user or not verify_password(formdata.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=30))

    return {"access_token": access_token, "token_type": "Bearer"}

@router.patch("/deactivate-activate-account")
async def deactivate_reactivate_account(current_user: Users = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    
    user = await get_user_by_email(current_user.email, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="user not found")
    if not user.is_active:
        await activate_user(current_user, db)
        return {"message": "account activated successfully"}
    if user.is_active:
        await deactivate_user(current_user, db)
        return{"message":"account activated successfully"}
        

