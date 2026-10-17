from email.policy import HTTP
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import user as model
from database import get_db
from schemas.users import UserCreate, UserPublic, UserUpdate, UserPrivate, Token

from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

from auth import create_access_token, hash_password, verify_password, CurrentUser

from config import settings

router = APIRouter()

@router.post("", 
        response_model=UserPrivate, 
        status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(model.User).where(func.lower(model.User.username) == user.username.lower())
    )
    existing_user = result.scalars().first() 

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    result = await db.execute(
        select(model.User).where(func.lower(model.User.email) == user.email.lower())
    )
    existing_email = result.scalars().first() 

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )

    new_user = model.User(
        username=user.username,
        email=user.email.lower(),
        password_hash=hash_password(user.password)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(model.User).where(func.lower(model.User.email) == form_data.username.lower()),
    )
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")

@router.get("/me", response_model=UserPrivate)
async def get_current_user(
    current_user: CurrentUser
):
    return current_user

@router.get("", 
        response_model=list[UserPublic])
async def get_users(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(model.User)
    )

    users = result.scalars().all()

    if users:
        return users

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found")
    

@router.get("/{user_id}", 
        response_model=UserPublic)
async def get_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(model.User).where(model.User.id == user_id)
    )
    user = result.scalars().first()

    if user:
        return user

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

@router.patch("/{user_id}", response_model=UserPrivate)
async def update_user_partial(user_id: int,
                user_data:UserUpdate,
                current_user: CurrentUser,
                db: Annotated[AsyncSession, Depends(get_db)]):
    
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    result = await db.execute(
        select(model.User).where(model.User.id == user_id)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user_data.username is not None and user_data.username.lower() != user.username.lower():
        result = await db.execute(
            select(model.User).where(func.lower(model.User.username) == user_data.username.lower())
        )
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

    if user_data.email is not None and user_data.email.lower() != user.email.lower():
        result = await db.execute(
            select(model.User).where(func.lower(model.User.email) == user_data.email.lower())
        )
        existing_email = result.scalars().first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )

    if user_data.username is not None:
        user.username = user_data.username
    if user_data.email is not None:
        user.email = user_data.email.lower()

    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int,
                current_user: CurrentUser,
                db: Annotated[AsyncSession, Depends(get_db)]):

    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user"
        )

    result = await db.execute(
        select(model.User).where(model.User.id == user_id)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await db.delete(user)
    await db.commit()
