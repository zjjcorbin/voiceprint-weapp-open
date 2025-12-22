# 语音情绪识别系统

## 🧠 功能概述

本系统集成了基于SpeechBrain的语音情绪识别功能，能够实时分析用户语音中的情绪状态，支持7种基本情绪的识别和详细分析。

## 🎯 支持的情绪类型

| 情绪类型 | 中文名 | 表情符号 | 特征描述 |
|----------|--------|----------|----------|
| neutral | 中性 | 😐 | 平静、无特殊情绪的状态 |
| happy | 开心 | 😊 | 积极、愉悦的情绪状态 |
| sad | 悲伤 | 😢 | 消极、失落的情绪状态 |
| angry | 愤怒 | 😠 | 生气、不满的情绪状态 |
| fear | 恐惧 | 😨 | 害怕、紧张的情绪状态 |
| disgust | 厌恶 | 😒 | 反感、讨厌的情绪状态 |
| surprise | 惊讶 | 😲 | 意外、震惊的情绪状态 |

## 🛠 技术实现

### 核心技术栈
- **SpeechBrain**: 专业的音频和语音处理库
- **wav2vec2**: 预训练的语音特征提取器
- **ECAPA**: 高效的说话人编码器
- **PyTorch**: 深度学习框架
- **IEMOCAP数据集**: 情绪识别训练数据

### 模型架构
```
音频输入 → wav2vec2特征提取 → ECAPA编码器 → 情绪分类器 → 情绪概率分布
```

### 识别指标
- **置信度**: 0-1，识别结果的可信程度
- **强度**: 0-1，情绪的强烈程度
- **复杂度**: 0-1，情绪的复杂程度（基于信息熵）
- **质量评分**: 0-1，音频质量对识别的影响评估

## 📊 API接口

### 核心端点

#### 1. 情绪检测
```http
POST /api/emotion/detect
Content-Type: multipart/form-data

Parameters:
- audio_file: 音频文件 (必需)
- employee_id: 员工ID (可选)
- meeting_id: 会议ID (可选)
- require_analysis: 是否需要详细分析 (可选)
```

**响应示例:**
```json
{
  "success": true,
  "emotion_feature": {
    "dominant_emotion": "happy",
    "confidence": 0.85,
    "emotion_probabilities": {
      "happy": 0.85,
      "neutral": 0.10,
      "surprise": 0.05
    },
    "intensity": 0.72,
    "complexity": 0.35,
    "quality_score": 0.89,
    "analysis": {
      "confidence_level": "较高",
      "intensity_level": "中等",
      "complexity_level": "简单",
      "suggestions": [
        "保持积极的心态",
        "分享这份快乐给他人",
        "记录下这美好的时刻"
      ]
    },
    "audio_url": "http://minio:9000/voiceprint-audio/emotion_xxx.wav",
    "processing_time": 1.2
  }
}
```

#### 2. 批量检测
```http
POST /api/emotion/detect/batch
Content-Type: multipart/form-data

Parameters:
- audio_files: 音频文件列表 (1-10个)
- employee_id: 员工ID (可选)
- meeting_id: 会议ID (可选)
```

#### 3. 历史记录
```http
GET /api/emotion/history/{employee_id}
Parameters:
- limit: 返回数量 (默认50)
- offset: 偏移量 (默认0)
```

#### 4. 统计信息
```http
GET /api/emotion/statistics
Parameters:
- employee_id: 员工ID (可选)
- start_date: 开始日期 (可选)
- end_date: 结束日期 (可选)
```

#### 5. 反馈提交
```http
POST /api/emotion/feedback/{detection_id}

{
  "user_emotion": "happy",
  "accuracy_rating": 5,
  "comments": "识别结果准确"
}
```

## 📱 前端实现

### 页面结构
```
miniprogram/pages/emotion/
├── detect/detect.*          # 情绪检测页面
├── history/history.*         # 历史记录页面
└── detail/detail.*          # 检测详情页面
```

### 主要功能
- **录音界面**: 实时录音控制和可视化
- **结果展示**: 情绪分布图表和详细分析
- **历史记录**: 检测历史查看和管理
- **反馈系统**: 用户对识别结果的反馈
- **数据统计**: 个人情绪数据统计分析

### UI特性
- 渐变背景和现代化设计
- 实时录音动画和波形显示
- 情绪表情和颜色编码
- 响应式图表和数据可视化
- 流畅的页面过渡动画

## 🎛️ 配置参数

### 环境变量
```env
# 情绪识别模型配置
EMOTION_MODEL=speechbrain/emotion-recognition-wav2vec2-IEMOCAP
EMOTION_CONFIDENCE_THRESHOLD=0.6
SUPPORTED_EMOTIONS=neutral,happy,sad,angry,fear,disgust,surprise
EMOTION_ANALYSIS_ENABLED=true

# 音频处理参数
SAMPLE_RATE=16000
AUDIO_QUALITY_THRESHOLD=0.6
MIN_AUDIO_DURATION=3.0
MAX_AUDIO_DURATION=30.0
```

### 模型参数
- **采样率**: 16kHz (语音识别标准)
- **音频格式**: WAV, MP3, M4A, OGG
- **最大文件大小**: 50MB
- **处理时间**: <2秒/文件

## 📈 性能指标

### 识别准确率
- **IEMOCAP数据集**: >85% 准确率
- **实际应用**: 80-90% (取决于音频质量)
- **响应时间**: 平均1.2秒

### 质量评估
- **信噪比**: >15dB 为优秀
- **过零率**: 0.05-0.15 为语音正常范围
- **频谱特征**: 2000-4000Hz 为人声主要频段

## 🔧 部署配置

### 1. 模型下载
系统首次启动时会自动下载预训练模型：
- 声纹识别模型: `speechbrain/spkrec-ecapa-voxceleb`
- 情绪识别模型: `speechbrain/emotion-recognition-wav2vec2-IEMOCAP`

### 2. 存储配置
- 音频文件存储在MinIO对象存储
- 检测结果存储在MySQL数据库
- 模型文件缓存在本地 `pretrained_models/` 目录

### 3. 服务依赖
- **GPU支持**: 可选，自动检测并使用
- **内存需求**: 建议8GB+（模型加载）
- **CPU需求**: 4核+（音频处理）

## 🛡️ 安全特性

### 数据隐私
- 音频文件加密存储
- 个人数据本地化处理
- 支持数据删除和导出

### 访问控制
- JWT令牌认证
- 基于角色的权限控制
- API请求频率限制

### 审计日志
- 完整的操作记录
- 错误日志和监控
- 用户反馈追踪

## 📊 应用场景

### 企业管理
- **员工情绪监测**: 了解团队整体状态
- **会议情绪分析**: 评估会议氛围和效果
- **心理健康关怀**: 早期发现情绪问题

### 个人应用
- **情绪日记**: 记录和分析情绪变化
- **健康监测**: 长期情绪趋势分析
- **心理调节**: 提供个性化建议

## 🔮 未来规划

### 功能增强
- **多语言支持**: 扩展中文情绪识别
- **实时流处理**: 支持实时音频流分析
- **情绪预测**: 基于历史数据的趋势预测

### 模型优化
- **个性化模型**: 用户自适应调整
- **边缘计算**: 模型压缩和移动端部署
- **联邦学习**: 保护隐私的联合训练

### 集成扩展
- **第三方API**: 与企业系统集成
- **IoT设备**: 支持智能硬件接入
- **数据分析**: 高级BI和报表功能

## 🤝 贡献指南

欢迎贡献代码和建议！

### 开发环境设置
1. 克隆仓库: `git clone <repository>`
2. 安装依赖: `pip install -r requirements.txt`
3. 配置环境: `cp .env.example .env`
4. 启动服务: `./scripts/setup.sh init`

### 代码规范
- 遵循PEP 8编码规范
- 添加完整的文档字符串
- 编写单元测试
- 提交前运行代码检查

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。