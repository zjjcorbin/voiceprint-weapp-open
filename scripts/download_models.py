#!/usr/bin/env python3
"""
下载预训练模型脚本 - 检查已存在文件避免重复下载
"""

import os
import sys

def check_voiceprint_model_exists():
    """检查声纹模型是否已存在"""
    model_path = "pretrained_models/spkrec-ecapa-voxceleb"
    
    if not os.path.exists(model_path):
        return False
    
    key_files = [
        "hyperparams.yaml",
        "custom.yaml",
        "embedding_model.ckpt"
    ]
    
    for file_name in key_files:
        file_path = os.path.join(model_path, file_name)
        if not os.path.exists(file_path):
            return False
    
    return True

def check_emotion_model_exists(emotion_model_name):
    """检查情绪模型是否已存在"""
    save_dir = f"emotion_recognition_{emotion_model_name.split('/')[-1]}"
    model_path = f"pretrained_models/{save_dir}"
    
    if not os.path.exists(model_path):
        return False
    
    key_files = [
        "hyperparams.yaml",
        "custom.yaml",
        "tok.emb",
        "embedding_model.ckpt"
    ]
    
    for file_name in key_files:
        file_path = os.path.join(model_path, file_name)
        if not os.path.exists(file_path):
            return False
    
    return True

def download_models():
    """下载声纹和情绪识别模型"""
    print("预训练模型下载脚本")
    print("=" * 50)
    
    # 设置Hugging Face镜像
    os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
    print("使用国内镜像: https://hf-mirror.com")
    
    # 导入配置
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from app.core.config import settings
    
    voiceprint_model = "speechbrain/spkrec-ecapa-voxceleb"
    emotion_model = settings.EMOTION_MODEL
    
    print(f"声纹识别模型: {voiceprint_model}")
    print(f"情绪识别模型: {emotion_model}")
    print("=" * 50)
    
    models_downloaded = True
    
    try:
        # 导入SpeechBrain
        try:
            from speechbrain.inference.speaker import SpeakerRecognition
            from speechbrain.inference.classifiers import EncoderClassifier
        except ImportError:
            from speechbrain.pretrained import SpeakerRecognition
            from speechbrain.pretrained import EncoderClassifier
        
        # 检查声纹模型
        if check_voiceprint_model_exists():
            print("[SKIP] 声纹识别模型已存在，跳过下载")
        else:
            print("[DOWNLOAD] 开始下载声纹识别模型...")
            print("使用国内镜像加速下载...")
            os.makedirs("pretrained_models/spkrec-ecapa-voxceleb", exist_ok=True)
            
            spk_model = SpeakerRecognition.from_hparams(
                source=voiceprint_model,
                savedir="pretrained_models/spkrec-ecapa-voxceleb",
                run_opts={"device": "cpu"}  # 下载时使用CPU避免GPU内存问题
            )
            print("[OK] 声纹识别模型下载完成")
        
        # 检查情绪模型
        save_dir = f"emotion_recognition_{emotion_model.split('/')[-1]}"
        if check_emotion_model_exists(emotion_model):
            print("[SKIP] 情绪识别模型已存在，跳过下载")
        else:
            print("[DOWNLOAD] 开始下载情绪识别模型...")
            print("使用国内镜像加速下载...")
            os.makedirs(f"pretrained_models/{save_dir}", exist_ok=True)
            
            try:
                emo_model = EncoderClassifier.from_hparams(
                    source=emotion_model,
                    savedir=f"pretrained_models/{save_dir}",
                    run_opts={"device": "cpu"}  # 下载时使用CPU避免GPU内存问题
                )
                print(f"[OK] 情绪识别模型 {emotion_model} 下载完成")
            except Exception as e:
                print(f"[FAIL] 情绪识别模型下载失败: {e}")
                print("系统将在首次运行时自动尝试下载模型")
                models_downloaded = False
        
        print("=" * 50)
        if models_downloaded:
            print("[OK] 所有模型下载/检查完成！")
            print("已下载模型:")
            print(f"  - 声纹识别: {voiceprint_model}")
            print(f"  - 情绪识别: {emotion_model}")
        else:
            print("[WARN] 部分模型下载失败，系统运行时可能需要重新下载")
        
        return models_downloaded
        
    except ImportError as e:
        print(f"[FAIL] 模块导入错误: {e}")
        print("请确保已安装SpeechBrain: pip install speechbrain")
        return False
        
    except Exception as e:
        print(f"[FAIL] 模型下载失败: {e}")
        print("系统将在首次运行时自动下载模型")
        return False

if __name__ == "__main__":
    success = download_models()
    sys.exit(0 if success else 1)