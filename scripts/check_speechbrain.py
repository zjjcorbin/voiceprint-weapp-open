#!/usr/bin/env python3
"""
检查SpeechBrain安装状态和可用模块
"""

import sys
import importlib
import pkg_resources

def check_speechbrain():
    """检查SpeechBrain安装状态"""
    print("检查SpeechBrain安装状态...")
    
    try:
        import speechbrain
        print(f"✓ SpeechBrain已安装，版本: {speechbrain.__version__}")
        return True
    except ImportError:
        print("✗ SpeechBrain未安装")
        return False

def check_modules():
    """检查可用模块"""
    print("\n检查SpeechBrain模块...")
    
    modules_to_check = [
        "speechbrain.inference.speaker",
        "speechbrain.inference.classifiers", 
        "speechbrain.inference.encoders",
        "speechbrain.lobes.models.huggingface_transformers.wav2vec2"
    ]
    
    available_modules = []
    
    for module_name in modules_to_check:
        try:
            importlib.import_module(module_name)
            print(f"✓ {module_name}")
            available_modules.append(module_name)
        except ImportError as e:
            print(f"✗ {module_name} - {e}")
    
    return available_modules

def test_imports():
    """测试具体导入"""
    print("\n测试具体导入...")
    
    tests = [
        {
            "name": "SpeakerRecognition (inference)",
            "import": "from speechbrain.inference.speaker import SpeakerRecognition"
        },
        {
            "name": "SpeakerRecognition (pretrained)", 
            "import": "from speechbrain.pretrained import SpeakerRecognition"
        },
        {
            "name": "EncoderClassifier (inference)",
            "import": "from speechbrain.inference.classifiers import EncoderClassifier"
        },
        {
            "name": "EncoderClassifier (pretrained)",
            "import": "from speechbrain.pretrained import EncoderClassifier"
        },
        {
            "name": "MelSpectrogramEncoder (inference)",
            "import": "from speechbrain.inference.encoders import MelSpectrogramEncoder"
        },
        {
            "name": "MelSpectrogramEncoder (CRNN)",
            "import": "from speechbrain.lobes.models.CRNN import MelSpectrogramEncoder"
        }
    ]
    
    working_imports = []
    
    for test in tests:
        try:
            exec(test["import"])
            print(f"✓ {test['name']}")
            working_imports.append(test["import"])
        except ImportError as e:
            print(f"✗ {test['name']} - {e}")
    
    return working_imports

def show_recommendations(available_modules, working_imports):
    """显示建议"""
    print("\n建议的导入方式：")
    
    if "from speechbrain.inference.speaker import SpeakerRecognition" in working_imports:
        print("• from speechbrain.inference.speaker import SpeakerRecognition")
    elif "from speechbrain.pretrained import SpeakerRecognition" in working_imports:
        print("• from speechbrain.pretrained import SpeakerRecognition")
    
    if "from speechbrain.inference.classifiers import EncoderClassifier" in working_imports:
        print("• from speechbrain.inference.classifiers import EncoderClassifier")
    elif "from speechbrain.pretrained import EncoderClassifier" in working_imports:
        print("• from speechbrain.pretrained import EncoderClassifier")

def main():
    """主函数"""
    print("SpeechBrain诊断工具")
    print("=" * 50)
    
    # 检查安装
    if not check_speechbrain():
        print("\n解决方案:")
        print("pip install speechbrain")
        return False
    
    # 检查模块
    available_modules = check_modules()
    
    # 测试导入
    working_imports = test_imports()
    
    # 显示建议
    show_recommendations(available_modules, working_imports)
    
    return len(working_imports) > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)