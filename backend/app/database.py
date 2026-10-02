"""数据库连接管理"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database

from app.config import settings

# SQLAlchemy 同步引擎（用于创建表等操作）
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM 模型基类
Base = declarative_base()

# databases 异步数据库（用于 FastAPI 异步查询）
database = Database(settings.database_url.replace("+pymysql", ""))


async def get_db():
    """获取数据库连接（依赖注入）"""

    yield database
