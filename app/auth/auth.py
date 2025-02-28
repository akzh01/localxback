import os
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
from app.config.database import db
from typing import Optional

# 📌 Загружаем переменные из .env
load_dotenv()

# 🔑 Секретный ключ и настройки JWT
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")  # Загружаем ключ из .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Срок жизни токена (в минутах)

# 🔐 Настройки хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ⏭️ OAuth2 схема авторизации (используется в Swagger UI)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

# 🔹 Хеширование пароля
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# 🔹 Проверка пароля
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# 🔹 Создание JWT-токена
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 🔍 Декодирование JWT
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# 🔐 Получение текущего пользователя из JWT
async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = await db.users.find_one({"email": payload["sub"]})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return {"id": str(user["_id"]), "email": user["email"], "role": user.get("role", "user")}

# 🔐 Проверка, является ли пользователь админом
async def get_admin_user(token: str = Depends(oauth2_scheme)):
    user = await get_current_user(token)
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return user