const app = getApp()

Page({
  data: {
    verificationStatus: 'idle', // idle, recording, processing, success, fail
    isRecording: false,
    hasRecording: false,
    processing: false,
    recordingDuration: 0,
    waveformData: [],
    verificationResult: null,
    verificationHistory: [],
    isRegistered: false,
    recordingTimer: null,
    animationTimer: null
  },

  onLoad() {
    this.loadRegistrationStatus()
    this.loadVerificationHistory()
  },

  onShow() {
    // 每次显示时刷新注册状态
    this.loadRegistrationStatus()
  },

  onUnload() {
    this.cleanup()
  },

  // 加载注册状态
  async loadRegistrationStatus() {
    try {
      const res = await app.request({
        url: `${app.globalData.baseUrl}/voiceprint/status`,
        method: 'GET'
      })

      if (res.success) {
        this.setData({
          isRegistered: res.data.registered
        })
      }
    } catch (error) {
      console.error('加载注册状态失败:', error)
    }
  },

  // 加载验证历史
  async loadVerificationHistory() {
    try {
      const res = await app.request({
        url: `${app.globalData.baseUrl}/voiceprint/history`,
        method: 'GET'
      })

      if (res.success) {
        const history = res.data.slice(0, 5).map(item => ({
          ...item,
          time: this.formatTime(item.createdAt)
        }))
        
        this.setData({
          verificationHistory: history
        })
      }
    } catch (error) {
      console.error('加载验证历史失败:', error)
    }
  },

  // 开始录音
  async startRecording() {
    if (this.data.processing || this.data.isRecording) return

    // 检查是否已注册
    if (!this.data.isRegistered) {
      wx.showModal({
        title: '未注册声纹',
        content: '您还未注册声纹，请先进行声纹注册',
        showCancel: true,
        confirmText: '去注册',
        success: (res) => {
          if (res.confirm) {
            this.goToRegister()
          }
        }
      })
      return
    }

    try {
      await app.startRecording({
        duration: 10000, // 最长10秒
        frameSize: 50
      })
      
      this.setData({
        isRecording: true,
        hasRecording: false,
        recordingDuration: 0,
        verificationStatus: 'recording',
        waveformData: this.generateWaveformData(),
        verificationResult: null
      })

      // 开始计时
      this.setData({
        recordingTimer: setInterval(() => {
          this.setData({
            recordingDuration: this.data.recordingDuration + 1
          })
          
          // 更新波形数据
          this.updateWaveformData()
        }, 100)
      })

    } catch (error) {
      wx.showToast({
        title: error.message || '录音失败',
        icon: 'none'
      })
    }
  },

  // 停止录音
  stopRecording() {
    if (!this.data.isRecording) return
    
    app.stopRecording()
    
    if (this.data.recordingTimer) {
      clearInterval(this.data.recordingTimer)
      this.setData({ recordingTimer: null })
    }
    
    this.setData({
      isRecording: false,
      verificationStatus: 'processing',
      processing: true
    })

    // 延迟处理录音结果
    setTimeout(() => {
      this.handleRecordingResult()
    }, 500)
  },

  // 处理录音结果
  async handleRecordingResult() {
    const lastRecording = app.globalData.lastRecording
    
    if (!lastRecording || !lastRecording.tempFilePath) {
      this.setData({
        verificationStatus: 'fail',
        processing: false
      })
      
      wx.showToast({
        title: '录音失败，请重试',
        icon: 'none'
      })
      return
    }

    if (lastRecording.duration < 2000) {
      this.setData({
        verificationStatus: 'fail',
        processing: false
      })
      
      wx.showModal({
        title: '录音时间太短',
        content: '录音时间至少需要2秒，请重新录制',
        showCancel: false,
        confirmText: '确定'
      })
      return
    }

    try {
      // 上传音频文件
      const uploadRes = await app.uploadFile(lastRecording.tempFilePath, {
        type: 'verify'
      })

      if (uploadRes.success) {
        // 进行声纹验证
        const verifyRes = await app.request({
          url: `${app.globalData.baseUrl}/voiceprint/verify`,
          method: 'POST',
          data: {
            audioFile: uploadRes.data.filePath
          }
        })

        this.setData({
          processing: false,
          hasRecording: true,
          recordingDuration: 0
        })

        if (verifyRes.success && verifyRes.data.match) {
          // 验证成功
          this.setData({
            verificationStatus: 'success',
            verificationResult: {
              success: true,
              userName: verifyRes.data.userName,
              confidence: verifyRes.data.confidence,
              verifyTime: this.formatDateTime(new Date())
            }
          })
          
          // 刷新历史记录
          this.loadVerificationHistory()
        } else {
          // 验证失败
          this.setData({
            verificationStatus: 'fail',
            verificationResult: {
              success: false,
              message: verifyRes.message || '无法识别您的身份'
            }
          })
        }
      } else {
        throw new Error(uploadRes.message || '上传失败')
      }
    } catch (error) {
      this.setData({
        verificationStatus: 'fail',
        processing: false,
        verificationResult: {
          success: false,
          message: error.message || '验证失败'
        }
      })
    }
  },

  // 重新验证
  retry() {
    this.setData({
      verificationResult: null,
      verificationStatus: 'idle',
      hasRecording: false,
      recordingDuration: 0,
      waveformData: []
    })
  },

  // 关闭结果
  closeResult() {
    this.setData({
      verificationResult: null,
      verificationStatus: 'idle',
      hasRecording: false,
      recordingDuration: 0,
      waveformData: []
    })
  },

  // 获取状态图标
  getStatusIcon() {
    switch (this.data.verificationStatus) {
      case 'idle':
        return '🎤'
      case 'recording':
        return '🎙️'
      case 'processing':
        return '⏳'
      case 'success':
        return '✅'
      case 'fail':
        return '❌'
      default:
        return '🎤'
    }
  },

  // 获取状态标题
  getStatusTitle() {
    switch (this.data.verificationStatus) {
      case 'idle':
        return '准备验证'
      case 'recording':
        return '正在录音'
      case 'processing':
        return '识别中'
      case 'success':
        return '验证成功'
      case 'fail':
        return '验证失败'
      default:
        return '准备验证'
    }
  },

  // 获取状态描述
  getStatusDesc() {
    switch (this.data.verificationStatus) {
      case 'idle':
        return '请按住下方按钮开始录音'
      case 'recording':
        return '请说出任意内容'
      case 'processing':
        return '正在分析您的声音特征'
      case 'success':
        return '身份验证成功'
      case 'fail':
        return '无法识别您的身份，请重试'
      default:
        return '请按住下方按钮开始录音'
    }
  },

  // 获取录音提示
  getRecordingTip() {
    if (this.data.isRecording) {
      return '松开按钮结束录音'
    } else if (this.data.hasRecording) {
      return '录音已完成，正在识别...'
    } else {
      return '录音时长建议3-8秒'
    }
  },

  // 生成波形数据
  generateWaveformData() {
    return Array.from({ length: 20 }, () => {
      return Math.floor(Math.random() * 40) + 20
    })
  },

  // 更新波形数据
  updateWaveformData() {
    if (!this.data.isRecording) return

    const newData = Array.from({ length: 20 }, () => {
      return Math.floor(Math.random() * 60) + 20
    })

    this.setData({
      waveformData: newData
    })
  },

  // 查看全部历史
  viewAllHistory() {
    wx.navigateTo({
      url: '/pages/profile/profile'
    })
  },

  // 跳转到注册页面
  goToRegister() {
    wx.redirectTo({
      url: '/pages/voiceprint/register/register'
    })
  },

  // 跳转到会议管理
  goToMeeting() {
    wx.switchTab({
      url: '/pages/meeting/list/list'
    })
  },

  // 清理资源
  cleanup() {
    if (this.data.recordingTimer) {
      clearInterval(this.data.recordingTimer)
    }
    if (this.data.animationTimer) {
      clearInterval(this.data.animationTimer)
    }
    if (this.data.isRecording) {
      app.stopRecording()
    }
  },

  // 格式化时间
  formatTime(timestamp) {
    const now = new Date()
    const time = new Date(timestamp)
    const diff = now - time
    
    if (diff < 60000) { // 1分钟内
      return '刚刚'
    } else if (diff < 3600000) { // 1小时内
      return Math.floor(diff / 60000) + '分钟前'
    } else if (diff < 86400000) { // 1天内
      return Math.floor(diff / 3600000) + '小时前'
    } else if (diff < 604800000) { // 1周内
      return Math.floor(diff / 86400000) + '天前'
    } else {
      return time.toLocaleDateString()
    }
  },

  // 格式化日期时间
  formatDateTime(date) {
    const year = date.getFullYear()
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const day = date.getDate().toString().padStart(2, '0')
    const hour = date.getHours().toString().padStart(2, '0')
    const minute = date.getMinutes().toString().padStart(2, '0')
    const second = date.getSeconds().toString().padStart(2, '0')
    return `${year}-${month}-${day} ${hour}:${minute}:${second}`
  }
})