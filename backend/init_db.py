"""本地初始化数据库表

用途：用 SQLAlchemy 直接从 ORM 模型建表（user / article / agent_log），
并补齐各字段的数据库默认值。也可改用 sql/create_table.sql 手动建表。

前置条件：
    1. MySQL 已启动，且已手动创建数据库：
       CREATE DATABASE ai_passage_creator CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    2. backend 目录已有 .env 且数据库连接信息正确

运行：
    uv run python init_db.py     （或 .venv\\Scripts\\python init_db.py）
"""

from app.database import Base, engine
from sqlalchemy import text

# 导入模型，让它们注册到 Base.metadata 上
from app.models import (  # noqa: F401
    AgentLog,
    Article,
    User,
)

# ORM 模型的 default= 是 Python 层默认值，不会写入数据库 DDL；
# 这里补齐各表字段的数据库默认值，避免原生 SQL INSERT 报 "Field doesn't have a default value"
_DEFAULT_FIX_STATEMENTS = [
    "ALTER TABLE article MODIFY createTime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP",
    "ALTER TABLE article MODIFY updateTime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
    "ALTER TABLE article MODIFY isDelete smallint NOT NULL DEFAULT 0",
    "ALTER TABLE article MODIFY status varchar(20) NOT NULL DEFAULT 'PENDING'",
    "ALTER TABLE article MODIFY phase varchar(40) NOT NULL DEFAULT 'PENDING'",
    "ALTER TABLE user MODIFY createTime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP",
    "ALTER TABLE user MODIFY editTime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP",
    "ALTER TABLE user MODIFY updateTime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
    "ALTER TABLE user MODIFY isDelete smallint NOT NULL DEFAULT 0",
    "ALTER TABLE user MODIFY userRole varchar(256) NOT NULL DEFAULT 'user'",
    "ALTER TABLE agent_log MODIFY createTime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP",
    "ALTER TABLE agent_log MODIFY startTime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP",
    "ALTER TABLE agent_log MODIFY updateTime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
    "ALTER TABLE agent_log MODIFY isDelete smallint NOT NULL DEFAULT 0",
]


def _fix_column_defaults() -> None:
    """补齐字段默认值（幂等，可重复执行）"""
    with engine.begin() as conn:
        for stmt in _DEFAULT_FIX_STATEMENTS:
            conn.execute(text(stmt))
    print("已补齐字段默认值")


def main() -> None:
    tables = list(Base.metadata.tables.keys())
    print(f"即将创建表: {', '.join(tables)}")
    Base.metadata.create_all(bind=engine)
    print("建表完成")
    _fix_column_defaults()


if __name__ == "__main__":
    main()
