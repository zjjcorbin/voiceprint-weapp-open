#!/usr/bin/env python3
"""
专门测试Wav2Vec2模型和依赖
"""

import sys
import importlib

def test_wav2vec2_dependencies():
    """测试Wav2Vec2相关依赖"""
    print("检查Wav2Vec2依赖...")
    
    dependencies = [
        "torch",
        "transformers", 
        "huggingface_hub",
        "speechbrain"
    ]
    
    for dep in dependencies:
        try:
            if dep == "huggingface_transformers":
                try:
                    import huggingface_transformers
                    print(f"✓ {dep}: {huggingface_transformers.__version__}")
                except ImportError:
                    print(f"✗ {dep}: 未安装")
            else:
                module = importlib.import_module(dep)
                if hasattr(module, '__version__'):
                    print(f"✓ {dep}: {module.__version__}")
                else:
                    print(f"✓ {dep}: 已安装")
        except ImportError as e:
            print(f"✗ {dep}: {e}")

def test_wav2vec2_classes():
    """测试Wav2Vec2相关类"""
    print("\n测试Wav2Vec2类...")
    
    tests = [
        ("transformers.Wav2Vec2Model", "from transformers import Wav2Vec2Model"),
        ("speechbrain.lobes.models.huggingface_transformers.wav2vec2.Wav2Vec2", 
         "from speechbrain.lobes.models.huggingface_transformers.wav2vec2 import Wav2Vec2"),
        ("speechbrain.lobes.models.huggingface_transformers", 
         "import speechbrain.lobes.models.huggingface_transformers"),
    ]
    
    for name, import_cmd in tests:
        try:
            exec(import_cmd)
            print(f"✓ {name}")
        except ImportError as e:
            print(f"✗ {name}: {e}")

def test_emotion_model():
    """测试情绪识别模型"""
    print("\n测试情绪识别模型...")
    
    try:
        try:
            from speechbrain.inference.classifiers import EncoderClassifier
        except ImportError:
            from speechbrain.pretrained import EncoderClassifier
        
        print("尝试加载 speechbrain/emotion-recognition-wav2vec2-IEMOCAP...")
        model = EncoderClassifier.from_hparams(
            source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
            savedir="test_emotion_wav2vec2",
            run_opts={"device": "cpu"}
        )
        print("✓ 模型加载成功！")
        return True
        
    except Exception as e:
        print(f"✗ 模型加载失败: {e}")
        
        # 尝试安装建议
        if "Wav2Vec2" in str(e):
            print("\n可能的解决方案：")
            print("1. 安装/更新 huggingface-transformers:")
            print("   pip install huggingface-transformers")
            print("2. 安装/更新 transformers:")
            print("   pip install --upgrade transformers")
            print("3. 尝试不同版本的SpeechBrain:")
            print("   pip install --upgrade speechbrain")
        
        return False

if __name__ == "__main__":
    print("Wav2Vec2 依赖和模型测试")
    print("=" * 50)
    
    test_wav2vec2_dependencies()
    test_wav2vec2_classes()
    success = test_emotion_model()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Wav2Vec2 模型可以正常使用！")
    else:
        print("⚠️ Wav2Vec2 模型有问题，请按照建议进行修复")
    
    sys.exit(0 if success else 1)