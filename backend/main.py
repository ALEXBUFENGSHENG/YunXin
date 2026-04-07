import os
from datetime import timedelta

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.api.router import api_router
from app.core.auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from app.spaced_api import router as memory_router
from mysql_storage import mysql_storage

load_dotenv()

app = FastAPI(title="AI 助教后端")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(memory_router)


class Token(BaseModel):
    access_token: str
    token_type: str
    username: str


class UserRegister(BaseModel):
    username: str
    password: str


@app.post("/api/auth/register", response_model=Token)
async def register(user: UserRegister):
    if not user.username or not user.password:
        raise HTTPException(status_code=400, detail="Username and password are required")
    success = mysql_storage.create_user(user.username, user.password)
    if not success:
        raise HTTPException(status_code=400, detail="Username already registered")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer", "username": user.username}


@app.post("/api/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = mysql_storage.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": form_data.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer", "username": form_data.username}


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "AI 助教服务运行正常"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8090)
