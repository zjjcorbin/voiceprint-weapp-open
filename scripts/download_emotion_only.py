#!/usr/bin/env python3
"""
精简模型下载脚本 - 只下载指定的情绪识别模型
"""

import os
import sys

def check_model_exists(save_dir):
    """检查模型文件是否已存在"""
    model_path = f"pretrained_models/{save_dir}"
    
    if not os.path.exists(model_path):
        return False
    
    # 检查关键文件是否存在
    key_files = [
        "hyperparams.yaml",
        "custom.yaml", 
        "tok.emb",
        "embedding_model.ckpt"
    ]
    
    for file_name in key_files:
        file_path = os.path.join(model_path, file_name)
        if not os.path.exists(file_path):
            print(f"缺少关键文件: {file_path}")
            return False
    
    return True

def download_emotion_model_only():
    """下载配置文件中指定的情绪识别模型"""
    # 添加项目根目录到Python路径
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 设置Hugging Face镜像
    os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
    
    from app.core.config import settings
    
    model_name = settings.EMOTION_MODEL
    save_dir = f"emotion_recognition_{model_name.split('/')[-1]}"
    model_path = f"pretrained_models/{save_dir}"
    
    print("情绪识别模型下载脚本")
    print("=" * 50)
    print(f"模型: {model_name}")
    print(f"保存目录: {model_path}")
    print("使用国内镜像: https://hf-mirror.com")
    print("=" * 50)
    
    # 检查模型是否已存在
    if check_model_exists(save_dir):
        print("检测到模型文件已存在，跳过下载")
        print("如需重新下载，请删除以下目录:")
        print(f"  {model_path}")
        print("=" * 50)
        return True
    
    print("开始下载情绪识别模型...")
    
    try:
        # 导入SpeechBrain
        try:
            from speechbrain.inference.classifiers import EncoderClassifier
        except ImportError:
            from speechbrain.pretrained import EncoderClassifier
        
        # 创建模型目录
        os.makedirs(model_path, exist_ok=True)
        
        print("正在从Hugging Face镜像下载模型...")
        print("这可能需要几分钟时间，请耐心等待...")
        
        # 下载模型
        model = EncoderClassifier.from_hparams(
            source=model_name,
            savedir=model_path,
            run_opts={"device": "cpu"}  # 下载时使用CPU避免GPU内存问题
        )
        
        print("=" * 50)
        print("[OK] 情绪识别模型下载成功！")
        print(f"模型: {model_name}")
        print(f"目录: {model_path}")
        print(f"配置文件: {settings.EMOTION_MODEL}")
        
        # 验证下载
        if check_model_exists(save_dir):
            print("[OK] 模型文件验证通过")
        else:
            print("[WARN] 模型文件验证失败，但下载可能已完成")
        
        print("=" * 50)
        return True
        
    except ImportError as e:
        print(f"模块导入错误: {e}")
        print("请确保已安装SpeechBrain: pip install speechbrain")
        return False
        
    except Exception as e:
        print(f"模型下载失败: {e}")
        print("请检查网络连接或磁盘空间")
        return False

def main():
    """主函数"""
    from app.core.config import settings
    
    print("精简模型下载脚本")
    print(f"下载模型: {settings.EMOTION_MODEL}")
    
    success = download_emotion_model_only()
    
    if success:
        print("\n下一步:")
        print("1. 运行测试脚本: python scripts/test_emotion_only.py")
        print("2. 启动应用: docker-compose up -d")
    else:
        print("\n请检查错误信息并重试")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)