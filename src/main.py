from fastapi import FastAPI, HTTPException, Request, status
from schemas import UserResponse, UserCreate

app = FastAPI()

users: list[dict] = [
    {
        "id": 1,
        "username": "nicobianca",
        "email": "nicobianca@mail.com"    
    },
    {
        "id": 2,
        "username": "juanpepe",
        "email": "juanpepe@mail.com"    
    },
]

@app.get("/", include_in_schema=False)
def home():
    return {"message": "Welcome..."}

@app.get("/api/users", response_model=list[UserResponse])
def get_users():
    return users;

@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_users(user_id: int):
    for user in users:
        if user.get("id") == user_id:
            return user
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

@app.post("/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    new_id = max(u["id"] for u in users) + 1 if users else 1
    new_user = {
        "id": new_id,
        "username": user.username,
        "email": user.email
    }
    users.append(new_user)
    return new_user