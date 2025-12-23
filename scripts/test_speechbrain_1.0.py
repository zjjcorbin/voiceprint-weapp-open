#!/usr/bin/env python3
"""
专门测试 SpeechBrain 1.0.x 版本
"""

import sys
import os

def test_speechbrain_1_0():
    """测试SpeechBrain 1.0.x 特性"""
    print("测试 SpeechBrain 1.0.x...")
    
    try:
        import speechbrain
        print(f"✓ SpeechBrain版本: {speechbrain.__version__}")
    except ImportError:
        print("✗ SpeechBrain未安装")
        return False
    
    # 测试新的inference模块
    print("\n测试新的inference模块...")
    
    try:
        from speechbrain.inference.speaker import SpeakerRecognition
        print("✓ speechbrain.inference.speaker.SpeakerRecognition")
    except ImportError as e:
        print(f"✗ speechbrain.inference.speaker.SpeakerRecognition: {e}")
    
    try:
        from speechbrain.inference.classifiers import EncoderClassifier
        print("✓ speechbrain.inference.classifiers.EncoderClassifier")
    except ImportError as e:
        print(f"✗ speechbrain.inference.classifiers.EncoderClassifier: {e}")
    
    try:
        from speechbrain.inference.encoders import MelSpectrogramEncoder
        print("✓ speechbrain.inference.encoders.MelSpectrogramEncoder")
    except ImportError as e:
        print(f"✗ speechbrain.inference.encoders.MelSpectrogramEncoder: {e}")
    
    # 测试Wav2Vec2相关模块
    print("\n测试Wav2Vec2相关模块...")
    
    try:
        from speechbrain.lobes.models.huggingface_transformers.wav2vec2 import Wav2Vec2
        print("✓ speechbrain.lobes.models.huggingface_transformers.wav2vec2.Wav2Vec2")
    except ImportError as e:
        print(f"✗ speechbrain.lobes.models.huggingface_transformers.wav2vec2.Wav2Vec2: {e}")
        print("  这通常意味着需要安装额外的依赖")
    
    return True

def test_emotion_models():
    """测试情绪识别模型"""
    print("\n测试情绪识别模型...")
    
    try:
        from speechbrain.inference.classifiers import EncoderClassifier
        
        # 测试不同的模型
        models = [
            "speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
            "speechbrain/emotion-identification-IEMOCAP",
            "speechbrain/emotion-recognition-cnn14-esc50"
        ]
        
        for model in models:
            try:
                print(f"  测试 {model}...")
                test_model = EncoderClassifier.from_hparams(
                    source=model,
                    savedir=f"test_{model.split('/')[-1]}",
                    run_opts={"device": "cpu"}
                )
                print(f"  ✓ {model} 加载成功")
                return model  # 返回第一个成功的模型
            except Exception as e:
                print(f"  ✗ {model} 失败: {str(e)[:80]}...")
                continue
        
        print("  所有情绪识别模型都失败")
        return None
        
    except ImportError as e:
        print(f"  情绪识别模块导入失败: {e}")
        return None

def test_speaker_models():
    """测试声纹识别模型"""
    print("\n测试声纹识别模型...")
    
    try:
        from speechbrain.inference.speaker import SpeakerRecognition
        
        model = "speechbrain/spkrec-ecapa-voxceleb"
        try:
            print(f"  测试 {model}...")
            test_model = SpeakerRecognition.from_hparams(
                source=model,
                savedir=f"test_{model.split('/')[-1]}",
                run_opts={"device": "cpu"}
            )
            print(f"  ✓ {model} 加载成功")
            return model
        except Exception as e:
            print(f"  ✗ {model} 失败: {str(e)[:80]}...")
            return None
        
    except ImportError as e:
        print(f"  声纹识别模块导入失败: {e}")
        return None

def main():
    """主函数"""
    print("SpeechBrain 1.0.x 专门测试")
    print("=" * 50)
    
    # 基础测试
    if not test_speechbrain_1_0():
        return False
    
    # 模型测试
    speaker_model = test_speaker_models()
    emotion_model = test_emotion_models()
    
    print("\n" + "=" * 50)
    print("测试总结:")
    print(f"  声纹识别: {'✓ 可用' if speaker_model else '✗ 不可用'}")
    print(f"  情绪识别: {'✓ 可用' if emotion_model else '✗ 不可用'}")
    
    if speaker_model and emotion_model:
        print("\n🎉 所有功能都可用！")
        print(f"推荐模型组合:")
        print(f"  声纹: {speaker_model}")
        print(f"  情绪: {emotion_model}")
    elif speaker_model:
        print("\n✅ 声纹识别可用，情绪识别不可用")
        print("系统可以正常运行声纹识别功能")
    else:
        print("\n❌ 声纹识别不可用，请检查安装")
    
    return speaker_model is not None

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)