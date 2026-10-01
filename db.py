# db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# sqlite数据库就是磁盘上一个叫chat.db的文件
SQLITE_DATABASE_URL = "sqlite:///./chat.db"

# 创建数据库大门（引擎）
engine = create_engine(
    SQLITE_DATABASE_URL,
    connect_args={"check_same_thread": False}  #engine 对象里面已经完整保存了数据库路径 + 文件名！钥匙 (engine) 上已经写好仓库名字了！不需要在建表的时候再传一遍文件名！
)

# 笔记本工厂：以后每次想要笔记本就从这里生产出来一本Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)#后面是工厂函数Session 会话：干活！增删改查都靠 Session。相当于一次和数据库的会话，干完活提交

# 所有数据表类的父类
Base = declarative_base()  #等之后models里面的每个类继承它的时候 就会登记到Base的花名册metadata里面从而就知道了这个表的结构


# 后面接口要用的函数，现在测试暂时不用管它
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
