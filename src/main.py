from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import engine
from routers import users

@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    #Shutdown
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

app.include_router(users.router, prefix="/api/users", tags=["users"])

@app.get("/", include_in_schema=False)
def home():
    return {"message": "Welcome..."}

