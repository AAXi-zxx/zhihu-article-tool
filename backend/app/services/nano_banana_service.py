"""AI 生图服务"""

import base64
import logging
from typing import Optional

from openai import AsyncOpenAI

from app.config import settings
from app.constants.article import ArticleConstant
from app.models.enums import ImageMethodEnum
from app.services.image_search_service import ImageSearchService
from app.schemas.image import ImageData, ImageRequest

logger = logging.getLogger(__name__)


class NanoBananaService(ImageSearchService):
    """AI 生图服务（OpenAI 兼容 images 接口，如智谱 CogView）"""

    def __init__(self):
        self.api_key = settings.nano_banana_api_key
        self.model = settings.nano_banana_model
        self.size = settings.nano_banana_image_size
        # 初始化 OpenAI 兼容客户端（生图）
        self.client = AsyncOpenAI(
            api_key=settings.nano_banana_api_key,
            base_url=settings.nano_banana_base_url,
        )

    async def search_image(self, keywords: str) -> Optional[str]:
        """此方法已废弃，请使用 get_image_data()"""
        return None

    async def get_image_data(self, request: ImageRequest) -> Optional[ImageData]:
        """获取图片数据"""
        prompt = request.get_effective_param(True)
        return await self.generate_image_data(prompt)

    async def generate_image_data(self, prompt: str) -> Optional[ImageData]:
        """
        根据提示词生成图片数据

        Args:
            prompt: 生图提示词

        Returns:
            ImageData 包含图片字节数据，生成失败返回 None
        """
        try:
            logger.info(
                f"AI 生图开始, model={self.model}, size={self.size}, prompt={prompt[:80]}"
            )

            # 调用 OpenAI 兼容的图片生成接口
            resp = await self.client.images.generate(
                model=self.model,
                prompt=prompt,
                size=self.size,
                n=1,
            )

            data = resp.data[0] if resp.data else None
            if not data:
                logger.error("AI 生图响应为空")
                return None

            # 部分服务返回 b64_json，部分返回 url
            if getattr(data, "b64_json", None):
                image_bytes = base64.b64decode(data.b64_json)
                logger.info(f"AI 生图成功, size={len(image_bytes)} bytes")
                return ImageData.from_bytes(image_bytes, "image/png")

            if getattr(data, "url", None):
                logger.info(f"AI 生图成功, url={data.url}")
                return ImageData.from_url(data.url)

            logger.error("AI 生图响应中未找到图片数据")
            return None
        except Exception as e:
            logger.error(f"AI 生图异常: {e}")
            return None

    def get_method(self) -> ImageMethodEnum:
        """获取图片服务类型"""
        return ImageMethodEnum.NANO_BANANA

    def get_fallback_image(self, position: int) -> str:
        """获取降级图片"""
        return ArticleConstant.PICSUM_URL_TEMPLATE.format(position)
