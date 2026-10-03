"""腾讯云 COS 服务"""

import logging
import httpx
import uuid
from typing import Optional
from qcloud_cos import CosConfig, CosS3Client
from io import BytesIO

from app.config import settings
from app.schemas.image import ImageData, DataType

logger = logging.getLogger(__name__)


class CosService:
    """腾讯云 COS 服务"""
    
    def __init__(self):
        # 初始化 COS 客户端
        config = CosConfig(
            Region=settings.tencent_cos_region,
            SecretId=settings.tencent_cos_secret_id,
            SecretKey=settings.tencent_cos_secret_key,
            Scheme='https'
        )
        self.client = CosS3Client(config)
        self.bucket = settings.tencent_cos_bucket
        self.region = settings.tencent_cos_region
        # 直连客户端：国内图片源（bing/ucloud 等）优先走直连，不受系统代理抖动影响
        self.http_client = httpx.AsyncClient(timeout=30.0, trust_env=False)
        # 代理客户端：外网图片源（pexels 等）直连不通时走系统代理兜底
        self.proxy_http_client = httpx.AsyncClient(timeout=30.0)
    
    async def _download_image_bytes(self, url: str) -> Optional[bytes]:
        """下载图片字节：先直连（国内源），失败后走系统代理（外源如 Pexels）"""
        try:
            response = await self.http_client.get(url)
            if response.status_code == 200 and response.content:
                return response.content
            logger.warning(f"直连下载图片失败({response.status_code}), 尝试代理: {url[:80]}")
        except Exception as e:
            logger.warning(f"直连下载图片异常({e}), 尝试代理: {url[:80]}")

        try:
            response = await self.proxy_http_client.get(url)
            if response.status_code == 200 and response.content:
                return response.content
            logger.error(f"代理下载图片失败({response.status_code}): {url[:80]}")
        except Exception as e:
            logger.error(f"代理下载图片异常: {e}")
        return None

    async def upload_image(self, image_url: str, folder: str) -> str:
        """
        上传图片到 COS
        
        Args:
            image_url: 图片 URL
            folder: 文件夹
            
        Returns:
            COS 图片 URL
        """
        try:
            # 下载图片（直连优先，代理兜底）
            image_bytes = await self._download_image_bytes(image_url)
            if not image_bytes:
                logger.error(f"下载图片失败: {image_url}")
                return None

            # 生成文件名
            import uuid
            file_name = f"{folder}/{uuid.uuid4()}.jpg"

            # 上传到 COS
            self.client.put_object(
                Bucket=self.bucket,
                Body=BytesIO(image_bytes),
                Key=file_name,
                ContentType='image/jpeg'
            )

            # 返回访问 URL
            return f"https://{self.bucket}.cos.{self.region}.myqcloud.com/{file_name}"
        except Exception as e:
            logger.error(f"上传图片到 COS 失败: {e}")
            return None
    
    async def upload_image_data(
        self,
        image_data: ImageData,
        folder: str
    ) -> Optional[str]:
        """
        上传图片数据到 COS
        支持多种数据格式：字节数据、URL、data URL
        
        Args:
            image_data: 图片数据
            folder: 文件夹
            
        Returns:
            COS 图片 URL
        """
        if not image_data or not image_data.is_valid():
            logger.warning("图片数据无效")
            return None
        
        try:
            # 1. 获取图片字节数据
            if image_data.data_type == DataType.BYTES:
                image_bytes = image_data.bytes
            elif image_data.data_type == DataType.DATA_URL:
                image_bytes = image_data.get_image_bytes()
            elif image_data.data_type == DataType.URL:
                # 下载图片（直连优先，代理兜底）；失败返回 None 走降级方案，
                # 避免把用户浏览器打不开的原始外链（如 Pexels）塞进文章造成裂图
                image_bytes = await self._download_image_bytes(image_data.url)
                if not image_bytes:
                    logger.error(f"下载图片失败: {image_data.url}")
                    return None
            else:
                logger.error(f"未知的数据类型: {image_data.data_type}")
                return None
            
            if not image_bytes:
                logger.error("图片字节数据为空")
                return None
            
            # 2. 生成文件名
            extension = image_data.get_file_extension()
            file_name = f"{folder}/{uuid.uuid4()}{extension}"
            
            # 3. 上传到 COS
            self.client.put_object(
                Bucket=self.bucket,
                Body=BytesIO(image_bytes),
                Key=file_name,
                ContentType=image_data.mime_type
            )
            
            # 4. 返回访问 URL
            cos_url = f"https://{self.bucket}.cos.{self.region}.myqcloud.com/{file_name}"
            logger.info(f"图片上传成功, size={len(image_bytes)} bytes, cosUrl={cos_url}")
            
            return cos_url
        except Exception as e:
            logger.error(f"上传图片数据到 COS 失败: {e}")
            # 下载/上传失败统一返回 None 走上层降级，不返回原始外链（避免裂图）
            return None
    
    def use_direct_url(self, image_url: str) -> str:
        """
        直接使用图片 URL（不上传到 COS）
        
        Args:
            image_url: 图片 URL
            
        Returns:
            图片 URL
        """
        return image_url
    
    async def close(self):
        """关闭 HTTP 客户端"""
        await self.http_client.aclose()
        await self.proxy_http_client.aclose()
