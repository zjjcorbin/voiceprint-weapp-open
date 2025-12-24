from minio import Minio
from minio.error import S3Error
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
    """测试MinIO连接并自动创建Bucket"""
    try:
        buckets = minio_client.list_buckets()
        bucket_names = [bucket.name for bucket in buckets]
        logger.info(f"MinIO connection successful. Available buckets: {bucket_names}")
        
        # 自动创建配置的Bucket（如果不存在）
        if settings.MINIO_BUCKET not in bucket_names:
            logger.info(f"Creating bucket: {settings.MINIO_BUCKET}")
            minio_client.make_bucket(settings.MINIO_BUCKET)
            logger.info(f"Bucket '{settings.MINIO_BUCKET}' created successfully.")
        else:
            logger.info(f"Bucket '{settings.MINIO_BUCKET}' already exists.")
        return True
    except S3Error as e:
        logger.error(f"MinIO S3 error during connection/test: {e}")
        return False
    except Exception as e:
        logger.error(f"MinIO connection failed: {e}")
        return False

# 初始化时测试连接
test_minio_connection()