# 声纹识别微信小程序

## 📱 功能概述

这是声纹识别系统的微信小程序前端，提供完整的声纹注册、验证和会议管理功能。

## 🏗️ 小程序架构

### 页面结构
```
pages/
├── index/            # 首页 - 功能入口和快速操作
├── login/            # 登录页 - 微信授权登录
├── voiceprint/       # 声纹相关功能
│   ├── register/     # 声纹注册页面
│   └── verify/       # 声纹验证页面
├── meeting/          # 会议管理
│   ├── list/         # 会议列表
│   ├── create/       # 创建会议
│   └── detail/       # 会议详情
└── profile/          # 个人中心
```

### 核心文件说明

#### app.js - 小程序入口
- 全局配置和状态管理
- 微信登录逻辑
- 录音功能封装
- 网络请求封装

#### app.json - 小程序配置
- 页面路由配置
- TabBar设置
- 权限配置

#### app.wxss - 全局样式
- 通用样式定义
- 组件样式规范
- 响应式设计

## 🎯 核心功能

### 1. 声纹注册 (pages/voiceprint/register/)
**功能特点：**
- 3步式注册流程引导
- 实时录音质量检测
- 波形可视化展示
- 多样本录制管理

**关键文件：**
- `register.js` - 注册逻辑
- `register.wxml` - 注册界面
- `register.wxss` - 注册样式

### 2. 声纹验证 (pages/voiceprint/verify/)
**功能特点：**
- 实时声纹匹配
- 置信度显示
- 历史记录查看
- 验证状态反馈

**关键文件：**
- `verify.js` - 验证逻辑
- `verify.wxml` - 验证界面
- `verify.wxss` - 验证样式

### 3. 会议管理 (pages/meeting/)
**功能特点：**
- 会议创建和管理
- 实时录音控制
- 发言者识别
- 会议记录查看

**关键文件：**
- `list.js` - 会议列表逻辑
- `list.wxml` - 会议列表界面
- `list.wxss` - 会议列表样式

### 4. 个人中心 (pages/profile/)
**功能特点：**
- 用户信息管理
- 声纹状态查看
- 验证历史统计
- 系统设置

**关键文件：**
- `profile.js` - 个人中心逻辑
- `profile.wxml` - 个人中心界面
- `profile.wxss` - 个人中心样式

## 🔧 技术实现

### 1. 录音功能
```javascript
// 全局录音管理器
const recorderManager = wx.getRecorderManager()

// 开始录音
await app.startRecording({
  duration: 10000,
  sampleRate: 16000,
  numberOfChannels: 1,
  encodeBitRate: 96000,
  format: 'mp3'
})

// 停止录音
app.stopRecording()
```

### 2. 网络请求
```javascript
// 封装的请求方法
const res = await app.request({
  url: `${app.globalData.baseUrl}/api/voiceprint/verify`,
  method: 'POST',
  data: {
    audioFile: filePath
  }
})
```

### 3. 文件上传
```javascript
// 文件上传封装
const uploadRes = await app.uploadFile(audioFilePath, {
  type: 'register',
  sampleIndex: 1
})
```

### 4. 状态管理
```javascript
// 全局状态
globalData: {
  baseUrl: 'http://localhost:8000/api',
  userInfo: null,
  token: null,
  recordingManager: null
}
```

## 🎨 UI/UX设计

### 1. 设计规范
- **主色调**: #007AFF (微信蓝)
- **辅助色**: #52c41a (成功绿), #ff4d4f (警告红)
- **字体**: 系统默认字体栈
- **圆角**: 8rpx, 16rpx, 24rpx 规范

### 2. 组件样式
```css
/* 通用卡片 */
.card {
  background: white;
  border-radius: 16rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
}

/* 通用按钮 */
.btn {
  height: 80rpx;
  border-radius: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
}
```

### 3. 响应式设计
- 使用rpx单位适配不同屏幕
- 安全区域适配
- 横竖屏兼容

## 📱 使用流程

### 1. 首次使用流程
```
启动小程序 → 微信登录 → 声纹注册 → 声纹验证 → 开始使用
```

### 2. 日常使用流程
```
打开小程序 → 快速验证 → 查看会议记录 → 管理个人信息
```

### 3. 会议使用流程
```
创建会议 → 开始录音 → 实时识别 → 查看记录 → 导出报告
```

## 🔐 权限管理

### 1. 必需权限
- `scope.record` - 录音权限
- `scope.userInfo` - 用户信息

### 2. 权限申请
```javascript
// 录音权限申请
wx.getSetting({
  success: (res) => {
    if (!res.authSetting['scope.record']) {
      wx.authorize({
        scope: 'scope.record',
        success: () => {
          // 权限获取成功
        }
      })
    }
  }
})
```

### 3. 权限处理
- 友好的权限拒绝提示
- 重新授权引导
- 功能降级处理

## 🛠️ 开发配置

### 1. 开发环境
```javascript
// miniprogram/app.js
globalData: {
  baseUrl: 'http://localhost:8000/api', // 开发环境
}
```

### 2. 生产环境
```javascript
// miniprogram/app.js
globalData: {
  baseUrl: 'https://your-domain.com/api', // 生产环境
}
```

### 3. 项目配置
```json
{
  "appid": "wx1234567890abcdef",
  "projectname": "voiceprint-weapp-open",
  "libVersion": "2.24.0",
  "setting": {
    "urlCheck": true,
    "es6": true,
    "enhance": true
  }
}
```

## 📊 数据交互

### 1. 用户认证
```javascript
// 微信登录
const loginData = await app.wxLogin()
// 存储 token 和用户信息
```

### 2. 声纹注册
```javascript
// 上传音频文件
const uploadRes = await app.uploadFile(tempFilePath, {
  type: 'register',
  sampleIndex: index
})

// 提交注册
const registerRes = await app.request({
  url: '/voiceprint/register',
  method: 'POST',
  data: {
    recordings: recordings
  }
})
```

### 3. 声纹验证
```javascript
// 上传验证音频
const uploadRes = await app.uploadFile(audioPath, {
  type: 'verify'
})

// 获取验证结果
const verifyRes = await app.request({
  url: '/voiceprint/verify',
  method: 'POST',
  data: {
    audioFile: uploadRes.data.filePath
  }
})
```

## 🎯 性能优化

### 1. 图片优化
- 使用webp格式
- 懒加载实现
- 图片压缩

### 2. 代码优化
- 分包加载
- 组件复用
- 防抖节流

### 3. 网络优化
- 请求缓存
- 并发控制
- 超时处理

## 🐛 错误处理

### 1. 网络错误
```javascript
// 网络请求失败处理
catch: (err) => {
  wx.showToast({
    title: '网络请求失败',
    icon: 'none'
  })
}
```

### 2. 权限错误
```javascript
// 权限被拒绝处理
fail: () => {
  wx.showModal({
    title: '需要权限',
    content: '请允许使用录音功能',
    showCancel: false
  })
}
```

### 3. 系统错误
```javascript
// 系统级错误处理
wx.onError((err) => {
  console.error('小程序错误:', err)
  // 上报错误日志
})
```

## 📱 兼容性

### 1. 版本支持
- 微信版本: 7.0.0+
- 基础库: 2.10.0+

### 2. 设备支持
- iOS: 10.0+
- Android: 5.0+

### 3. 功能降级
- 低版本适配
- 功能开关
- 优雅降级

## 🔄 更新日志

### v1.0.0
- ✅ 基础声纹注册功能
- ✅ 声纹验证功能
- ✅ 会议管理功能
- ✅ 个人中心功能

### v1.1.0 (计划中)
- 🔄 UI优化
- 🔄 性能优化
- 🔄 新增统计功能
- 🔄 修复已知问题

## 📞 技术支持

如有技术问题，请联系：
- 📧 邮箱:csgyp@189.cn
- 🐛 问题反馈: [GitHub Issues](https://github.com/zjjcorbin/voiceprint-weapp-open/issues)

---

⭐ 如果这个小程序对您有帮助，请给我们一个Star！