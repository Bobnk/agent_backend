import logging
import sys

def setup_logger():
    # 创建一个日志对象，名字叫agent_backend
    logger = logging.getLogger("agent_backend")
    logger.setLevel(logging.INFO)

    # 防止重复添加处理器（复制代码记住这两行）
    if logger.handlers:
        return logger

    # 设置往控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    # 日志打印出来的文字格式：时间 名字 级别 消息
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# 生成全局日志对象，后面别的文件直接导入 logger 就可以打印
logger = setup_logger()
