from minio import Minio
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# 创建MinIO客户端实例
minio_client = Minio(
    endpoint=settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE
)

def test_minio_connection():
    """测试MinIO连接"""
    try:
        buckets = minio_client.list_buckets()
        logger.info(f"MinIO connection successful. Available buckets: {[bucket.name for bucket in buckets]}")
        return True
    except Exception as e:
        logger.error(f"MinIO connection failed: {e}")
        return False

# 初始化时测试连接
test_minio_connection()