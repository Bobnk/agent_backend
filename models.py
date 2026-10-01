# models.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from db import Base


class ChatHistory(Base):
    # __tablename__：数据库里面这张表格叫 chat_history
    __tablename__ = "chat_history"

    # id：每一行记录的唯一编号，自动增加
    id = Column(Integer, primary_key=True, index=True)
    # session_id：会话编号，同一轮聊天编号一样
    session_id = Column(String(64), index=True, comment="会话编号")
    # 用户提问，可以存很长文字所以用Text
    user_query = Column(Text, comment="用户提问")
    # AI的回答
    llm_answer = Column(Text, comment="AI回答")
    # 创建时间，保存这条记录的时候自动记录当前时间
    create_time = Column(DateTime, default=datetime.now, comment="保存时间")
    #当其他代码import这段代码后这个类的数据表格式就被base知道了 然后就建好了

# ----新增用户表----
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False) #存加密后的密码！不存明文！