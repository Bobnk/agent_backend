from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from db import get_db
from models import User
from pydantic import BaseModel


router = APIRouter(prefix="/user", tags=["用户账号"])

# ========== JWT的配置（密钥、算法、过期时间）==========
# ⚠️正式上线的时候这个SECRET_KEY一定要改成自己随机的长字符串！不要直接用这个！
SECRET_KEY = "my‑secret‑key‑change‑it‑in‑production‑abcdef123456"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30   # token30分钟就过期，用户需要重新登录


# ==========密码加密工具实例==========
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅全局定义OAuth2Scheme，用于从请求头提取Bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


# --------Pydantic请求体模型---------
class UserCreate(BaseModel):
    username: str
    password: str


class LoginForm(BaseModel):
    username: str
    password: str


# --------工具函数：密码哈希、校验密码--------
def verify_password(plain_password, hashed_password):
    """校验：用户输入的明文密码 和数据库里面加密后的密码是否一致"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """接收明文密码，返回加密之后的哈希字符串，保存进数据库"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """生成JWT令牌！data里面放我们要存进去的数据，比如{"sub":"username"}"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ==========【重点！依赖函数 get_current_user】后面接口鉴权全靠它！==========
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据，请重新登录",
        headers={"WWW‑Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


# --------注册接口---------
@router.post("/register")
async def register(user_form: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user_form.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="该用户名已经被注册！")
    hash_pw = get_password_hash(user_form.password)
    new_user = User(username=user_form.username, hashed_password=hash_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg":"注册成功","username":new_user.username}


# --------登录接口---------
@router.post("/login")
async def login(form: LoginForm, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="用户名错误")
    if not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="密码错误")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type":"bearer"}
