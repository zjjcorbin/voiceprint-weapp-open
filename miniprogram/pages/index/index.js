const app = getApp()

Page({
  data: {
    userInfo: null,
    isRecording: false,
    recordingTime: 0,
    voiceprintStatus: {
      registered: false,
      sampleCount: 0,
      accuracy: 0
    },
    recentActivities: [],
    recordingTimer: null
  },

  onLoad() {
    this.setData({
      userInfo: app.globalData.userInfo
    })
    
    if (app.globalData.userInfo) {
      this.loadVoiceprintStatus()
      this.loadRecentActivities()
    }
  },

  onShow() {
    // 每次显示页面时更新数据
    this.setData({
      userInfo: app.globalData.userInfo
    })
    
    if (app.globalData.userInfo) {
      this.loadVoiceprintStatus()
      this.loadRecentActivities()
    }
  },

  // 加载声纹状态
  async loadVoiceprintStatus() {
    try {
      const res = await app.request({
        url: `${app.globalData.baseUrl}/voiceprint/status`,
        method: 'GET'
      })

      if (res.success) {
        this.setData({
          voiceprintStatus: {
            registered: res.data.registered,
            sampleCount: res.data.sampleCount || 0,
            accuracy: res.data.accuracy || 0
          }
        })
      }
    } catch (error) {
      console.error('加载声纹状态失败:', error)
    }
  },

  // 加载最近活动
  async loadRecentActivities() {
    try {
      const res = await app.request({
        url: `${app.globalData.baseUrl}/user/recent-activities`,
        method: 'GET'
      })

      if (res.success) {
        this.setData({
          recentActivities: res.data.map(item => ({
            ...item,
            time: this.formatTime(item.createdAt)
          }))
        })
      }
    } catch (error) {
      console.error('加载最近活动失败:', error)
    }
  },

  // 微信登录
  async wxLogin() {
    wx.showLoading({
      title: '登录中...',
      mask: true
    })

    try {
      await app.wxLogin()
      this.setData({
        userInfo: app.globalData.userInfo
      })
      
      // 加载用户数据
      await this.loadVoiceprintStatus()
      await this.loadRecentActivities()
      
      wx.hideLoading()
      wx.showToast({
        title: '登录成功',
        icon: 'success'
      })
    } catch (error) {
      wx.hideLoading()
      wx.showToast({
        title: error.message || '登录失败',
        icon: 'none'
      })
    }
  },

  // 导航到声纹注册
  navigateToVoiceprint() {
    if (!this.checkLogin()) return
    
    wx.navigateTo({
      url: '/pages/voiceprint/register/register'
    })
  },

  // 导航到声纹验证
  navigateToVerify() {
    if (!this.checkLogin()) return
    
    wx.navigateTo({
      url: '/pages/voiceprint/verify/verify'
    })
  },

  // 导航到会议管理
  navigateToMeeting() {
    if (!this.checkLogin()) return
    
    wx.navigateTo({
      url: '/pages/meeting/list/list'
    })
  },

  // 快速验证
  async quickVerify() {
    if (!this.checkLogin()) return
    
    if (!this.data.voiceprintStatus.registered) {
      wx.showModal({
        title: '提示',
        content: '您还未注册声纹，请先进行声纹注册',
        showCancel: true,
        confirmText: '去注册',
        success: (res) => {
          if (res.confirm) {
            this.navigateToVoiceprint()
          }
        }
      })
      return
    }

    wx.showLoading({
      title: '准备录音...',
      mask: true
    })

    try {
      await app.startRecording({
        duration: 5000 // 5秒录音
      })
      
      wx.hideLoading()
      this.setData({ isRecording: true })
      
      // 5秒后自动停止
      setTimeout(() => {
        if (this.data.isRecording) {
          this.stopRecordingAndVerify()
        }
      }, 5000)
      
    } catch (error) {
      wx.hideLoading()
      wx.showToast({
        title: error.message || '录音失败',
        icon: 'none'
      })
    }
  },

  // 开始录音
  async startRecording() {
    if (!this.checkLogin()) return
    
    if (this.data.isRecording) return
    
    try {
      await app.startRecording({
        duration: 10000 // 最长10秒
      })
      
      this.setData({ 
        isRecording: true,
        recordingTime: 0 
      })
      
      // 开始计时
      this.setData({
        recordingTimer: setInterval(() => {
          this.setData({
            recordingTime: this.data.recordingTime + 1
          })
        }, 1000)
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
    
    // 清除计时器
    if (this.data.recordingTimer) {
      clearInterval(this.data.recordingTimer)
      this.setData({ recordingTimer: null })
    }
    
    this.setData({ 
      isRecording: false,
      recordingTime: 0 
    })
    
    // 延迟处理录音结果
    setTimeout(() => {
      this.handleRecordingResult()
    }, 500)
  },

  // 停止录音并验证
  stopRecordingAndVerify() {
    this.stopRecording()
  },

  // 处理录音结果
  async handleRecordingResult() {
    const lastRecording = app.globalData.lastRecording
    
    if (!lastRecording || !lastRecording.tempFilePath) {
      wx.showToast({
        title: '录音失败，请重试',
        icon: 'none'
      })
      return
    }

    if (lastRecording.duration < 2000) {
      wx.showToast({
        title: '录音时间太短，请录制至少2秒',
        icon: 'none'
      })
      return
    }

    wx.showLoading({
      title: '识别中...',
      mask: true
    })

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

        wx.hideLoading()
        
        if (verifyRes.success && verifyRes.data.match) {
          wx.showModal({
            title: '验证成功',
            content: `识别成功！匹配度：${(verifyRes.data.confidence * 100).toFixed(1)}%`,
            showCancel: false,
            confirmText: '确定'
          })
          
          // 刷新状态
          this.loadRecentActivities()
        } else {
          wx.showModal({
            title: '验证失败',
            content: verifyRes.message || '无法识别您的身份，请重试',
            showCancel: false,
            confirmText: '确定'
          })
        }
      }
    } catch (error) {
      wx.hideLoading()
      wx.showToast({
        title: error.message || '验证失败',
        icon: 'none'
      })
    }
  },

  // 检查登录状态
  checkLogin() {
    if (!app.globalData.userInfo) {
      wx.showModal({
        title: '请先登录',
        content: '使用此功能需要先登录',
        showCancel: true,
        confirmText: '去登录',
        success: (res) => {
          if (res.confirm) {
            this.wxLogin()
          }
        }
      })
      return false
    }
    return true
  },

  // 查看更多活动
  viewMore() {
    wx.navigateTo({
      url: '/pages/profile/profile'
    })
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

  // 页面卸载时清理
  onUnload() {
    if (this.data.recordingTimer) {
      clearInterval(this.data.recordingTimer)
    }
    if (this.data.isRecording) {
      app.stopRecording()
    }
  }
})