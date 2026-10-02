"""配置管理"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# 获取项目根目录（python-backend 目录）
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """应用配置（AI 核心创作流程）"""
    
    # 服务器配置
    server_port: int = 8567
    server_host: str = "0.0.0.0"
    
    # 数据库配置
    db_host: str
    db_port: int = 3306
    db_name: str
    db_user: str
    db_password: str
    
    # Redis 配置
    redis_host: str
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    
    # AI 配置（中科大 LLM 网关）
    dashscope_api_key: str
    dashscope_base_url: str = "https://api.llm.ustc.edu.cn/v1"
    dashscope_model: str = "qwen-chat"
    
    # Pexels 图片搜索
    pexels_api_key: str
    
    # 腾讯云 COS
    tencent_cos_secret_id: str
    tencent_cos_secret_key: str
    tencent_cos_region: str
    tencent_cos_bucket: str
    tencent_cos_domain: str = ""
    
    # AI 生图（智谱 CogView，OpenAI 兼容接口）
    nano_banana_api_key: str
    nano_banana_base_url: str = "https://open.bigmodel.cn/api/paas/v4"
    nano_banana_model: str = "cogview-3-flash"
    nano_banana_aspect_ratio: str = "16:9"
    nano_banana_image_size: str = "1024x1024"
    nano_banana_output_mime_type: str = "image/png"
    
    # Iconify 配置
    iconify_api_url: str = "https://api.iconify.design"
    iconify_search_limit: int = 10
    iconify_default_height: int = 64
    iconify_default_color: str = ""
    
    # 表情包配置
    emoji_pack_search_url: str = "https://cn.bing.com/images/async"
    emoji_pack_suffix: str = "表情包"
    emoji_pack_timeout: int = 10000
    
    # SVG 示意图配置
    svg_diagram_default_width: int = 800
    svg_diagram_default_height: int = 600
    svg_diagram_folder: str = "svg-diagrams"

    # 多智能体并行编排配置
    agent_image_max_concurrency: int = 3
    agent_image_fail_fast: bool = True

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def database_url(self) -> str:
        """获取数据库连接 URL"""
        return f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
    
    @property
    def redis_url(self) -> str:
        """获取 Redis 连接 URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


settings = Settings()
