from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.chat import router as chat_router
from settings import settings
import uvicorn
from logger import logger

from contextlib import asynccontextmanager
from fastapi import FastAPI
from db import engine, Base
import models   # ⚠️千万不要删掉！加载ORM模型！
from api.user import router as user_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 服务启动的时候执行这里
    logger.info("==== 后端服务开始启动 ====")
    logger.info("正在创建数据表……")
    Base.metadata.create_all(engine)
    logger.info("✅数据库初始化完毕！")

    yield   # 这里是服务运行期间

    # 关闭服务的时候执行这里
    logger.info("==== 后端服务正在关闭 ====")

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(chat_router)

app.include_router(user_router)
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=settings.SERVER_PORT)
