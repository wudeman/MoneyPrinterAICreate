import logging
import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# 获取项目根目录
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

# 导入配置
from app.config.config import _cfg

# 获取数据库配置
db_config = _cfg.get("database", {})
DB_HOST = db_config.get("host", "localhost")
DB_PORT = db_config.get("port", 3306)
DB_USER = db_config.get("user", "root")
DB_PASSWORD = db_config.get("password", "")
DB_NAME = db_config.get("db_name", "media")
DB_CHARSET = db_config.get("charset", "utf8mb4")

# 使用MySQL数据库
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset={DB_CHARSET}"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    echo=False,  # 设置为True可打印SQL语句，调试时有用
    pool_size=db_config.get("pool_size", 10),
    pool_pre_ping=db_config.get("pool_pre_ping", True),
    max_overflow=20
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


# 依赖注入函数，用于获取数据库会话
def get_db() -> Generator[Session, None, None]:
    """获取数据库会话的依赖函数"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库，创建所有表"""
    try:
        # 导入所有模型，确保它们被注册
        from app.models.llm_model import LLMModel
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logging.info("数据库表创建成功")
    except Exception as e:
        logging.error(f"数据库初始化失败: {e}")
        raise