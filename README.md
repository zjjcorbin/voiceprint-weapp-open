# 企业声纹识别系统 (开源版)

基于FastAPI、SpeechBrain、Librosa和WebRTC的企业级声纹识别解决方案，专为中小型企业设计，支持200人规模的员工声纹管理。

## 🎯 系统特点

### 🌟 核心功能
- **声纹注册**: 支持多样本声纹特征提取，自动质量评估
- **实时识别**: 高精度声纹匹配，支持会议场景多人识别
- **情绪识别**: 基于SpeechBrain的语音情绪分析，支持7种情绪识别
- **会议记录**: 自动识别发言人，记录发言内容和情绪状态
- **企业认证**: 基于微信的企业级身份认证
- **数据安全**: 本地部署，数据完全可控

### 🛠 技术栈
- **后端**: FastAPI + SQLAlchemy + Alembic
- **音频处理**: SpeechBrain + Librosa + WebRTC + PyTorch
- **情绪识别**: SpeechBrain Emotion Recognition (ECAPA + wav2vec2)
- **存储**: MySQL + MinIO对象存储
- **部署**: Docker + Docker Compose
- **监控**: Prometheus + Grafana (可选)

### 📊 性能指标
- **声纹识别准确率**: >95% (在理想环境下)
- **情绪识别准确率**: >85% (IEMOCAP数据集)
- **响应时间**: <2秒 (单个音频识别)
- **并发支持**: 10个并发识别任务
- **存储需求**: 每个声纹样本约100KB
- **支持情绪**: 中性、开心、悲伤、愤怒、恐惧、厌恶、惊讶 (7种情绪)

## 📱 项目结构

```
voiceprint-weapp-open/
├── app/                          # FastAPI后端应用
│   ├── main.py                   # 应用入口文件
│   ├── core/                     # 核心配置
│   │   └── config.py             # 配置管理
│   ├── models/                   # 数据模型
│   │   ├── emotion.py            # 情绪模型
│   │   ├── employee.py           # 员工模型
│   │   ├── voiceprint.py         # 声纹模型
│   │   └── ...                   # 其他模型
│   ├── routers/                  # API路由
│   │   ├── voiceprint.py         # 声纹相关API
│   │   ├── emotion.py            # 情绪识别API
│   │   ├── auth.py               # 认证API
│   │   └── ...                   # 其他路由
│   ├── services/                 # 业务服务层
│   │   ├── voiceprint_service.py # 声纹识别服务
│   │   ├── emotion_service.py    # 情绪识别服务
│   │   └── ...                   # 其他服务
│   └── schemas/                  # 数据验证模式
│       ├── voiceprint.py         # 声纹数据模型
│       ├── emotion.py            # 情绪数据模型
│       └── ...                   # 其他模型
├── database/                     # 数据库相关
│   └── schema.sql                # 数据库结构
├── miniprogram/                  # 微信小程序前端
│   ├── app.js                    # 小程序入口
│   ├── app.json                  # 小程序配置
│   ├── app.wxss                  # 全局样式
│   ├── project.config.json       # 项目配置
│   └── pages/                    # 页面文件
│       ├── index/                # 首页
│       │   ├── index.js
│       │   ├── index.wxml
│       │   └── index.wxss
│       ├── login/                # 登录页
│       │   ├── login.js
│       │   ├── login.wxml
│       │   └── login.wxss
│       ├── voiceprint/           # 声纹功能
│       │   ├── register/         # 声纹注册
│       │   │   ├── register.js
│       │   │   ├── register.wxml
│       │   │   └── register.wxss
│       │   └── verify/           # 声纹验证
│       │       ├── verify.js
│       │       ├── verify.wxml
│       │       └── verify.wxss
│       ├── emotion/              # 情绪识别
│       │   ├── detect/           # 情绪检测
│       │   │   ├── detect.js
│       │   │   ├── detect.wxml
│       │   │   └── detect.wxss
│       │   ├── history/          # 历史记录
│       │   │   ├── history.js
│       │   │   ├── history.wxml
│       │   │   └── history.wxss
│       │   └── detail/           # 检测详情
│       │       ├── detail.js
│       │       ├── detail.wxml
│       │       └── detail.wxss
│       ├── meeting/              # 会议管理
│       │   ├── list/             # 会议列表
│       │   │   ├── list.js
│       │   │   ├── list.wxml
│       │   │   └── list.wxss
│       │   ├── create/           # 创建会议
│       │   └── detail/           # 会议详情
│       └── profile/              # 个人中心
│           ├── profile.js
│           ├── profile.wxml
│           └── profile.wxss
├── scripts/                      # 部署脚本
│   └── setup.sh                  # 一键部署脚本
├── docker-compose.yml            # Docker编排
├── Dockerfile                    # Docker镜像
├── requirements.txt              # Python依赖
├── .env.example                  # 环境变量示例
└── README.md                     # 项目文档
```

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   微信小程序    │    │   Web管理界面   │    │   API接口       │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                      │
         └──────────────────────┼──────────────────────┘
                                │
         ┌──────────────────────┼──────────────────────┐
         │                      │                      │
┌────────▼────────┐   ┌────────▼────────┐   ┌────────▼────────┐
│   FastAPI       │   │   音频处理      │   │   数据存储      │
│   - 认证授权    │   │   - 声纹提取    │   │   - MySQL       │
│   - API接口     │   │   - 质量评估    │   │   - MinIO       │
│   - 业务逻辑    │   │   - 实时识别    │   │   - Redis缓存   │
└─────────────────┘   └─────────────────┘   └─────────────────┘
```

## 🚀 快速开始

### 环境要求
- **系统**: Linux/macOS/Windows (推荐Ubuntu 20.04+)
- **内存**: 最低4GB，推荐8GB+
- **存储**: 最低20GB可用空间
- **软件**: Docker 20.10+, Docker Compose 2.0+

### 一键部署

```bash
# 1. 克隆项目
git clone https://github.com/your-org/voiceprint-weapp-open.git
cd voiceprint-weapp-open

# 2. 初始化环境
chmod +x scripts/setup.sh
./scripts/setup.sh init

# 3. 启动服务
./scripts/setup.sh start

# 4. 查看状态
./scripts/setup.sh status
```

### 手动部署

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库、MinIO等参数

# 2. 启动基础服务
docker-compose up -d mysql minio redis

# 3. 等待数据库启动
sleep 30

# 4. 初始化数据库
docker-compose exec -T mysql mysql -u voiceprint -ppassword123 voiceprint_system < database/schema.sql

# 5. 启动API服务
docker-compose up -d voiceprint-api

# 6. 启动Nginx代理
docker-compose up -d nginx
```

### 验证部署

```bash
# 检查服务状态
curl http://localhost:8000/health

# 查看API文档
# 浏览器访问: http://localhost:8000/docs

# 检查MinIO控制台
# 浏览器访问: http://localhost:9001
```

## 📱 小程序配置

### 1. 修改配置
```javascript
// miniprogram/app.js
globalData: {
  baseUrl: 'http://localhost:8000/api', // 开发环境
  // baseUrl: 'https://your-domain.com/api', // 生产环境
}
```

### 2. 配置服务器域名
在微信公众平台添加以下域名到白名单：
- request: `https://your-domain.com`
- uploadFile: `https://your-domain.com`

### 3. 编译运行
使用微信开发者工具打开 `miniprogram` 目录，配置正确的AppID后编译运行。

## 🔧 API使用示例

### 声纹注册
```python
import requests

# 上传音频文件进行声纹注册
files = {'audio_file': open('voice.wav', 'rb')}
data = {
    'employee_id': 123,
    'sample_index': 1
}
headers = {'Authorization': 'Bearer YOUR_TOKEN'}

response = requests.post(
    'http://localhost:8000/api/voiceprint/register',
    files=files,
    data=data,
    headers=headers
)

print(response.json())
```

### 声纹识别
```python
# 上传音频文件进行声纹识别
files = {'audio_file': open('speech.wav', 'rb')}
data = {'meeting_id': 456}  # 可选
headers = {'Authorization': 'Bearer YOUR_TOKEN'}

response = requests.post(
    'http://localhost:8000/api/voiceprint/recognize',
    files=files,
    data=data,
    headers=headers
)

result = response.json()
if result['success']:
    print(f"识别成功: {result['identified_employee']}")
    print(f"置信度: {result['confidence']:.2f}")
else:
    print("识别失败")
```

### 情绪识别
```python
# 上传音频文件进行情绪识别
files = {'audio_file': open('speech.wav', 'rb')}
data = {
    'employee_id': 123,  # 可选
    'require_analysis': True  # 是否需要详细分析
}
headers = {'Authorization': 'Bearer YOUR_TOKEN'}

response = requests.post(
    'http://localhost:8000/api/emotion/detect',
    files=files,
    data=data,
    headers=headers
)

result = response.json()
if result['success']:
    emotion = result['emotion_feature']
    print(f"主要情绪: {emotion['dominant_emotion']}")
    print(f"置信度: {emotion['confidence']:.2f}")
    print(f"情绪强度: {emotion['intensity']:.2f}")
    print(f"情绪分布: {emotion['emotion_probabilities']}")
else:
    print("情绪检测失败")
```

## 🎛️ 配置说明

### 环境变量
```env
# 数据库配置
DATABASE_URL=mysql+asyncmy://voiceprint:password@localhost:3306/voiceprint_system

# MinIO配置
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=voiceprint-audio

# 声纹识别配置
VOICEPRINT_MODEL=speechbrain/spkrec-ecapa-voxceleb
VOICEPRINT_THRESHOLD=0.75
MIN_AUDIO_DURATION=3.0
MAX_AUDIO_DURATION=30.0

# 情绪识别配置
EMOTION_MODEL=speechbrain/emotion-recognition-wav2vec2-IEMOCAP
EMOTION_CONFIDENCE_THRESHOLD=0.6
AUDIO_QUALITY_THRESHOLD=0.6

# 微信小程序配置
WECHAT_APP_ID=your_app_id
WECHAT_APP_SECRET=your_app_secret
```

### 音频处理参数
```python
# 采样率配置
SAMPLE_RATE = 16000  # Hz

# 音频质量要求
AUDIO_QUALITY_THRESHOLD = 0.6  # 最低质量阈值
MIN_AUDIO_DURATION = 3.0  # 最小时长(秒)
MAX_AUDIO_DURATION = 30.0  # 最大时长(秒)

# 声纹识别参数
VOICEPRINT_THRESHOLD = 0.75  # 匹配阈值
MAX_VOICEPRINTS_PER_EMPLOYEE = 5  # 每人最大样本数
SAMPLE_COUNT_REQUIRED = 3  # 注册所需样本数

# 情绪识别参数
EMOTION_CONFIDENCE_THRESHOLD = 0.6  # 情绪识别置信度阈值
SUPPORTED_EMOTIONS = ['neutral', 'happy', 'sad', 'angry', 'fear', 'disgust', 'surprise']  # 支持的情绪
EMOTION_ANALYSIS_ENABLED = True  # 是否启用详细分析
```

## 🧠 情绪识别API

### 主要端点

#### POST `/api/emotion/detect` - 检测语音情绪
**请求参数:**
- `audio_file`: 音频文件 (必需)
- `employee_id`: 员工ID (可选)
- `meeting_id`: 会议ID (可选)  
- `require_analysis`: 是否需要详细分析 (可选, 默认true)

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
      "suggestions": ["保持积极的心态", "分享这份快乐给他人"]
    }
  }
}
```

#### GET `/api/emotion/history/{employee_id}` - 获取情绪历史
**查询参数:**
- `limit`: 返回记录数量 (默认50)
- `offset`: 偏移量 (默认0)

#### POST `/api/emotion/detect/batch` - 批量情绪检测
**请求参数:**
- `audio_files`: 音频文件列表 (1-10个文件)
- `employee_id`: 员工ID (可选)
- `meeting_id`: 会议ID (可选)

### 支持的情绪类型

| 情绪 | 中文名 | 表情 | 说明 |
|------|--------|------|------|
| neutral | 中性 | 😐 | 平静、无特殊情绪状态 |
| happy | 开心 | 😊 | 快乐、愉悦的情绪状态 |
| sad | 悲伤 | 😢 | 难过、失落的情绪状态 |
| angry | 愤怒 | 😠 | 生气、不满的情绪状态 |
| fear | 恐惧 | 😨 | 害怕、紧张的情绪状态 |
| disgust | 厌恶 | 😒 | 反感、讨厌的情绪状态 |
| surprise | 惊讶 | 😲 | 意外、震惊的情绪状态 |

### 情绪分析维度

1. **置信度 (Confidence)**: 0-1, 识别结果的可信程度
2. **强度 (Intensity)**: 0-1, 情绪的强烈程度
3. **复杂度 (Complexity)**: 0-1, 情绪的复杂程度，越接近1表示情绪越复杂
4. **质量评分 (Quality)**: 0-1, 音频质量评分，影响识别准确性

## 📊 监控和维护

### 查看服务状态
```bash
# 查看所有服务
docker-compose ps

# 查看服务日志
./scripts/setup.sh logs voiceprint-api
./scripts/setup.sh logs mysql
./scripts/setup.sh logs minio

# 重启服务
./scripts/setup.sh restart
```

### 数据备份
```bash
# 备份数据库
docker-compose exec mysql mysqldump -u voiceprint -ppassword123 \
    voiceprint_system > backup_$(date +%Y%m%d).sql

# 备份MinIO数据
docker cp voiceprint-minio:/data ./minio_backup_$(date +%Y%m%d)
```

### 性能监控
启用监控组件：
```bash
# 启动Prometheus和Grafana
docker-compose --profile monitoring up -d

# 访问Grafana
# 浏览器: http://localhost:3000
# 用户名: admin, 密码: admin123
```

## 🔍 故障排查

### 常见问题

**Q: API服务启动失败**
```bash
# 检查日志
./scripts/setup.sh logs voiceprint-api

# 常见原因：模型下载失败，手动下载模型
docker-compose exec voiceprint-api python -c "
from speechbrain.inference.speaker import SpeakerRecognition
model = SpeakerRecognition.from_hparams(
    source='speechbrain/spkrec-ecapa-voxceleb',
    savedir='pretrained_models/spkrec-ecapa-voxceleb'
)"
```

**Q: 数据库连接失败**
```bash
# 检查MySQL状态
docker-compose ps mysql

# 检查网络连接
docker-compose exec voiceprint-api ping mysql
```

**Q: MinIO访问失败**
```bash
# 检查MinIO状态
curl http://localhost:9000/minio/health/live

# 重置MinIO
docker-compose down minio
docker volume rm voiceprint-weapp-open_minio_data
docker-compose up -d minio
```

### 日志分析
```bash
# API应用日志
tail -f logs/app/app.log

# Nginx访问日志
tail -f logs/nginx/access.log

# MySQL慢查询日志
docker-compose exec mysql tail -f /var/log/mysql/slow.log
```

## 🛡️ 安全配置

### 生产环境安全建议

1. **修改默认密码**
   - MySQL用户密码
   - MinIO访问密钥
   - JWT密钥

2. **启用HTTPS**
   - 配置有效SSL证书
   - 强制HTTPS重定向

3. **网络隔离**
   - 使用防火墙限制端口访问
   - 配置内网访问控制

4. **数据加密**
   - 启用数据库传输加密
   - 敏感字段加密存储

### SSL证书配置
```bash
# 使用Let's Encrypt获取免费证书
certbot certonly --standalone -d your-domain.com

# 复制证书到nginx目录
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
```

## 📈 性能优化

### 数据库优化
```sql
-- 添加索引优化查询
CREATE INDEX idx_voiceprints_employee_active ON voiceprints(employee_id, is_active);
CREATE INDEX idx_speech_records_meeting_employee ON speech_records(meeting_id, employee_id);

-- 配置MySQL参数优化
SET GLOBAL innodb_buffer_pool_size = 512M;
SET GLOBAL max_connections = 200;
```

### 缓存策略
```python
# Redis缓存声纹特征
import redis
r = redis.Redis(host='redis', port=6379)

# 缓存声纹特征24小时
r.setex(f"voiceprint:{employee_id}", 86400, embedding_json)
```

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 技术支持

- 📧 邮箱: support@voiceprint-system.com
- 📱 微信: VoiceprintSupport
- 🐛 问题反馈: [GitHub Issues](https://github.com/your-org/voiceprint-weapp-open/issues)

## 🗺️ 发展路线图

### v1.1 (计划中)
- [ ] 支持多语言声纹识别
- [ ] 添加人脸识别多因子认证
- [ ] 实现分布式部署
- [ ] 增加AI会议纪要生成

### v1.2 (计划中)
- [ ] 支持实时流式识别
- [ ] 添加声音情绪分析
- [ ] 集成企业LDAP认证
- [ ] 支持语音命令控制

---

⭐ 如果这个项目对您有帮助，请给我们一个Star！