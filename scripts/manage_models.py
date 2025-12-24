#!/usr/bin/env python3
"""
模型管理脚本 - 检查、下载和管理预训练模型
使用国内镜像: https://hf-mirror.com
"""

import os
import sys
import argparse

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check_model_exists(model_path, model_type="general"):
    """检查模型文件是否已存在"""
    
    if not os.path.exists(model_path):
        return False, f"模型目录不存在: {model_path}"
    
    # 根据模型类型定义关键文件
    if model_type == "voiceprint":
        key_files = ["hyperparams.yaml", "custom.yaml", "embedding_model.ckpt"]
    elif model_type == "emotion":
        key_files = ["hyperparams.yaml", "custom.yaml", "tok.emb", "embedding_model.ckpt"]
    else:
        key_files = ["hyperparams.yaml"]  # 通用检查
    
    missing_files = []
    for file_name in key_files:
        file_path = os.path.join(model_path, file_name)
        if not os.path.exists(file_path):
            missing_files.append(file_name)
    
    if missing_files:
        return False, f"缺少关键文件: {', '.join(missing_files)}"
    
    return True, "模型文件完整"


def download_model(model_source, save_dir, model_type):
    """下载指定模型"""
    try:
        # 设置Hugging Face镜像
        os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
        
        # 导入SpeechBrain
        try:
            if model_type == "voiceprint":
                from speechbrain.inference.speaker import SpeakerRecognition
                model = SpeakerRecognition.from_hparams(
                    source=model_source, 
                    savedir=save_dir,
                    run_opts={"device": "cpu"}  # 下载时使用CPU避免GPU内存问题
                )
            elif model_type == "emotion":
                from speechbrain.inference.classifiers import EncoderClassifier
                model = EncoderClassifier.from_hparams(
                    source=model_source, 
                    savedir=save_dir,
                    run_opts={"device": "cpu"}  # 下载时使用CPU避免GPU内存问题
                )
            else:
                raise ValueError(f"不支持的模型类型: {model_type}")
        except ImportError:
            # 回退到旧版本
            if model_type == "voiceprint":
                from speechbrain.pretrained import SpeakerRecognition
                model = SpeakerRecognition.from_hparams(
                    source=model_source, 
                    savedir=save_dir,
                    run_opts={"device": "cpu"}
                )
            elif model_type == "emotion":
                from speechbrain.pretrained import EncoderClassifier
                model = EncoderClassifier.from_hparams(
                    source=model_source, 
                    savedir=save_dir,
                    run_opts={"device": "cpu"}
                )
        
        return True, f"模型 {model_source} 下载成功"
        
    except Exception as e:
        return False, f"模型下载失败: {e}"


def check_all_models():
    """检查所有模型状态"""
    print("检查模型状态...")
    print("=" * 60)
    
    try:
        from app.core.config import settings
        
        # 检查声纹模型
        voiceprint_model_path = "pretrained_models/spkrec-ecapa-voxceleb"
        vp_exists, vp_msg = check_model_exists(voiceprint_model_path, "voiceprint")
        print(f"声纹识别模型: {'[OK]' if vp_exists else '[FAIL]'} {vp_msg}")
        
        # 检查情绪模型
        emotion_model = settings.EMOTION_MODEL
        emotion_save_dir = f"pretrained_models/emotion_recognition_{emotion_model.split('/')[-1]}"
        emo_exists, emo_msg = check_model_exists(emotion_save_dir, "emotion")
        print(f"情绪识别模型: {'[OK]' if emo_exists else '[FAIL]'} {emo_msg}")
        
        print("=" * 60)
        
        if vp_exists and emo_exists:
            print("[OK] 所有模型已就绪，可以启动应用")
            return True
        else:
            print("[WARN] 部分模型缺失，运行 --download 下载")
            return False
            
    except Exception as e:
        print(f"[ERROR] 检查模型状态失败: {e}")
        return False


def download_all_models(force=False):
    """下载所有模型"""
    print("下载预训练模型...")
    print("=" * 60)
    print("使用国内镜像: https://hf-mirror.com")
    print("=" * 60)
    
    try:
        from app.core.config import settings
        
        # 声纹模型
        voiceprint_model = "speechbrain/spkrec-ecapa-voxceleb"
        voiceprint_path = "pretrained_models/spkrec-ecapa-voxceleb"
        
        vp_exists, vp_msg = check_model_exists(voiceprint_path, "voiceprint")
        if vp_exists and not force:
            print(f"[SKIP] 声纹识别模型已存在，跳过下载")
        else:
            if vp_exists and force:
                print(f"[FORCE] 强制重新下载声纹识别模型")
            else:
                print(f"[DOWNLOAD] 下载声纹识别模型...")
            
            os.makedirs(voiceprint_path, exist_ok=True)
            vp_success, vp_msg = download_model(voiceprint_model, voiceprint_path, "voiceprint")
            print(f"声纹识别模型: {'[OK]' if vp_success else '[FAIL]'} {vp_msg}")
        
        # 情绪模型
        emotion_model = settings.EMOTION_MODEL
        emotion_save_dir = f"pretrained_models/emotion_recognition_{emotion_model.split('/')[-1]}"
        
        emo_exists, emo_msg = check_model_exists(emotion_save_dir, "emotion")
        if emo_exists and not force:
            print(f"[SKIP] 情绪识别模型已存在，跳过下载")
        else:
            if emo_exists and force:
                print(f"[FORCE] 强制重新下载情绪识别模型")
            else:
                print(f"[DOWNLOAD] 下载情绪识别模型...")
            
            os.makedirs(emotion_save_dir, exist_ok=True)
            emo_success, emo_msg = download_model(emotion_model, emotion_save_dir, "emotion")
            print(f"情绪识别模型: {'[OK]' if emo_success else '[FAIL]'} {emo_msg}")
        
        print("=" * 60)
        print("下载完成，运行 --check 验证")
        
    except Exception as e:
        print(f"[ERROR] 下载模型失败: {e}")


def clean_models():
    """清理已下载的模型文件"""
    print("清理模型文件...")
    print("=" * 60)
    
    models_to_clean = [
        "pretrained_models/spkrec-ecapa-voxceleb",
        "pretrained_models/emotion_recognition_wav2vec2-IEMOCAP"
    ]
    
    for model_path in models_to_clean:
        if os.path.exists(model_path):
            import shutil
            try:
                shutil.rmtree(model_path)
                print(f"[OK] 已删除: {model_path}")
            except Exception as e:
                print(f"[FAIL] 删除失败: {model_path} - {e}")
        else:
            print(f"[SKIP] 不存在: {model_path}")
    
    print("=" * 60)
    print("清理完成")


def main():
    parser = argparse.ArgumentParser(description="模型管理脚本")
    parser.add_argument("--check", action="store_true", help="检查模型状态")
    parser.add_argument("--download", action="store_true", help="下载缺失的模型")
    parser.add_argument("--force", action="store_true", help="强制重新下载所有模型")
    parser.add_argument("--clean", action="store_true", help="清理已下载的模型")
    
    args = parser.parse_args()
    
    if not any([args.check, args.download, args.clean]):
        args.check = True  # 默认检查状态
    
    try:
        if args.clean:
            clean_models()
        elif args.download:
            download_all_models(force=args.force)
        elif args.check:
            success = check_all_models()
            if success:
                print("\n下一步: 启动应用")
                print("  docker-compose up -d")
                print("  或")
                print("  python -m uvicorn app.main:app")
            else:
                print("\n下一步: 下载缺失模型")
                print("  python scripts/manage_models.py --download")
    
    except KeyboardInterrupt:
        print("\n操作已取消")
    except Exception as e:
        print(f"\n[ERROR] 操作失败: {e}")


if __name__ == "__main__":
    main()