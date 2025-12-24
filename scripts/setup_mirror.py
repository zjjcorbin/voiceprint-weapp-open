#!/usr/bin/env python3
"""
设置Hugging Face镜像脚本
确保在应用启动前正确配置镜像地址
"""

import os
import sys

def setup_hf_mirror():
    """设置Hugging Face镜像"""
    # 检查是否需要使用镜像
    use_mirror = os.getenv("USE_HF_MIRROR", "false").lower() == "true"
    
    if use_mirror:
        # 设置Hugging Face镜像
        os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
        
        # 设置其他相关环境变量
        os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"  # 禁用hf-transfer，避免冲突
        os.environ["TRANSFORMERS_CACHE"] = os.path.join(os.getcwd(), "pretrained_models", "cache")
        
        print("✓ Hugging Face镜像已设置:")
        print(f"  HF_ENDPOINT: {os.environ['HF_ENDPOINT']}")
        print(f"  TRANSFORMERS_CACHE: {os.environ.get('TRANSFORMERS_CACHE')}")
        
        return True
    else:
        print("ℹ 未启用Hugging Face镜像，将使用原始地址")
        print("  如需启用，请设置环境变量: USE_HF_MIRROR=true")
        return False

def create_env_file():
    """创建包含镜像配置的.env文件"""
    env_file = ".env"
    env_example_file = ".env.example"
    
    if not os.path.exists(env_file) and os.path.exists(env_example_file):
        # 复制示例文件
        with open(env_example_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ 已创建 {env_file} 文件")
        return True
    
    elif os.path.exists(env_file):
        # 检查是否包含镜像配置
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "USE_HF_MIRROR=true" not in content:
            print("ℹ 建议在 .env 文件中添加以下配置:")
            print("  USE_HF_MIRROR=true")
            print("  HF_ENDPOINT=https://hf-mirror.com")
        else:
            print("✓ .env 文件已包含镜像配置")
        
        return True
    
    return False

def verify_mirror_connectivity():
    """验证镜像连接性"""
    try:
        import requests
        
        mirror_url = "https://hf-mirror.com"
        response = requests.get(mirror_url, timeout=5)
        
        if response.status_code == 200:
            print(f"✓ 镜像连接正常: {mirror_url}")
            return True
        else:
            print(f"⚠ 镜像响应异常: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"⚠ 镜像连接失败: {e}")
        return False

def main():
    """主函数"""
    print("Hugging Face镜像设置脚本")
    print("=" * 40)
    
    # 创建.env文件
    create_env_file()
    print()
    
    # 设置镜像
    mirror_enabled = setup_hf_mirror()
    print()
    
    # 验证连接
    if mirror_enabled:
        verify_mirror_connectivity()
    
    print("=" * 40)
    print("设置完成！")
    
    if mirror_enabled:
        print("\n接下来可以:")
        print("1. 下载模型: python scripts/download_models.py")
        print("2. 启动应用: python -m uvicorn app.main:app")
    else:
        print("\n如需启用镜像，请运行:")
        print("  export USE_HF_MIRROR=true")
        print("  或在 .env 文件中添加: USE_HF_MIRROR=true")

if __name__ == "__main__":
    main()