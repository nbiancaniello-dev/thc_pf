from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, status, Request
from contextlib import asynccontextmanager
from database import engine, get_db
from routers import users
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

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

@app.get("/health")
async def health_check(db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable"
        ) from exc
    return {"status": "healthy "}

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"

    if "Referrer-Policy" not in response.headers:
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    if request.url.hostname not in ("localhost", "127.0.0.1"):
        response.headers["Strict-Transport-Security"] = (
            "max-age=63072000; includeSubDomains"
        )

    return response