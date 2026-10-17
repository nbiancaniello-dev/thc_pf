from fastapi import FastAPI, HTTPException, Request, status, Depends
from schemas import UserResponse, UserCreate, UserUpdate
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import Session

import users.model as model
from database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/", include_in_schema=False)
def home():
    return {"message": "Welcome..."}

@app.get("/api/users", 
        response_model=list[UserResponse])
def get_users(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(model.User)
    )

    users = result.scalars().all()

    if users:
        return users

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found")
    

@app.get("/api/users/{user_id}", 
        response_model=UserResponse)
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(model.User).where(model.User.id == user_id)
    )
    user = result.scalars().first()

    if user:
        return user

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

@app.put("/api/users/{user_id}", 
        response_model=UserResponse)
def update_user_full(user_id: int, 
                user_data:UserUpdate, 
                db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(model.User).where(model.User.id == user_id)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.username = user_data.username
    user.email = user_data.email

    db.commit()
    db.refresh(user)
    return user

@app.patch("/api/users/{user_id}", 
        response_model=UserResponse)
def update_user_partial(user_id: int, 
                user_data:UserUpdate, 
                db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(model.User).where(model.User.id == user_id)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user

@app.post("/api/users", 
        response_model=UserResponse, 
        status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(model.User).where(model.User.username == user.username)
    )
    existing_user = result.scalars().first() 

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    result = db.execute(
        select(model.User).where(model.User.email == user.email)
    )
    existing_email = result.scalars().first() 

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )

    new_user = model.User(
        username=user.username,
        email=user.email
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.delete("/api/users/{user_id}", 
        status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(model.User).where(model.User.id == user_id)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(user)
    db.commit()
