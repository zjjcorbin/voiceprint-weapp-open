const app = getApp()

Page({
  data: {
    currentStep: 1,
    currentSampleIndex: 0,
    currentSampleText: '',
    isRecording: false,
    hasRecording: false,
    recordingDuration: 0,
    processing: false,
    recordings: [],
    waveformData: [],
    recordingTimer: null,
    animationTimer: null,
    
    // 示例文本库
    sampleTexts: [
      '今天是美好的一天，我很高兴来到这里',
      '语音识别技术正在改变我们的生活方式',
      '科技让世界变得更加美好和便利',
      '声纹识别是一种安全的身份验证方式',
      '人工智能技术在不断发展进步'
    ]
  },

  onLoad() {
    this.setData({
      currentSampleText: this.getRandomSampleText()
    })
  },

  onUnload() {
    this.cleanup()
  },

  // 获取随机示例文本
  getRandomSampleText() {
    const texts = this.data.sampleTexts
    return texts[Math.floor(Math.random() * texts.length)]
  },

  // 更换示例文本
  changeSampleText() {
    this.setData({
      currentSampleText: this.getRandomSampleText()
    })
  },

  // 下一步
  nextStep() {
    this.setData({
      currentStep: this.data.currentStep + 1
    })
    
    if (this.data.currentStep === 2) {
      this.startWaveformAnimation()
    }
  },

  // 切换录音状态
  async toggleRecording() {
    if (this.data.processing) return

    if (this.data.isRecording) {
      this.stopRecording()
    } else {
      await this.startRecording()
    }
  },

  // 开始录音
  async startRecording() {
    try {
      await app.startRecording({
        duration: 15000, // 最长15秒
        frameSize: 50
      })
      
      this.setData({
        isRecording: true,
        hasRecording: false,
        recordingDuration: 0,
        waveformData: new Array(20).fill(10)
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
    app.stopRecording()
    
    if (this.data.recordingTimer) {
      clearInterval(this.data.recordingTimer)
      this.setData({ recordingTimer: null })
    }
    
    this.setData({
      isRecording: false
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
      wx.showToast({
        title: '录音失败，请重试',
        icon: 'none'
      })
      return
    }

    if (lastRecording.duration < 3000) {
      wx.showModal({
        title: '录音时间太短',
        content: '录音时间至少需要3秒，请重新录制',
        showCancel: false,
        confirmText: '确定'
      })
      return
    }

    this.setData({ processing: true })

    wx.showLoading({
      title: '处理中...',
      mask: true
    })

    try {
      // 上传音频文件
      const uploadRes = await app.uploadFile(lastRecording.tempFilePath, {
        type: 'register',
        sampleIndex: this.data.currentSampleIndex,
        text: this.data.currentSampleText
      })

      wx.hideLoading()

      if (uploadRes.success) {
        // 保存录音信息
        const newRecording = {
          filePath: uploadRes.data.filePath,
          duration: lastRecording.duration,
          text: this.data.currentSampleText,
          sampleIndex: this.data.currentSampleIndex,
          uploadTime: new Date().toISOString()
        }

        const recordings = [...this.data.recordings]
        recordings[this.data.currentSampleIndex] = newRecording

        this.setData({
          hasRecording: true,
          recordings: recordings,
          processing: false
        })

        wx.showToast({
          title: '录音完成',
          icon: 'success'
        })
      } else {
        throw new Error(uploadRes.message || '上传失败')
      }
    } catch (error) {
      wx.hideLoading()
      this.setData({ processing: false })
      wx.showToast({
        title: error.message || '处理失败',
        icon: 'none'
      })
    }
  },

  // 重新录音
  rerecord() {
    this.setData({
      hasRecording: false,
      recordingDuration: 0,
      waveformData: []
    })
  },

  // 播放录音
  playRecording() {
    const recording = this.data.recordings[this.data.currentSampleIndex]
    if (!recording || !recording.filePath) return

    const audioContext = wx.createInnerAudioContext()
    audioContext.src = recording.filePath
    audioContext.play()

    audioContext.onPlay(() => {
      console.log('开始播放录音')
    })

    audioContext.onError((res) => {
      console.error('播放录音失败:', res)
      wx.showToast({
        title: '播放失败',
        icon: 'none'
      })
    })
  },

  // 下一个样本
  async nextSample() {
    if (this.data.processing) return

    this.setData({ processing: true })

    wx.showLoading({
      title: '处理中...',
      mask: true
    })

    try {
      if (this.data.currentSampleIndex < 2) {
        // 下一个样本
        this.setData({
          currentSampleIndex: this.data.currentSampleIndex + 1,
          currentSampleText: this.getRandomSampleText(),
          hasRecording: false,
          recordingDuration: 0,
          waveformData: []
        })
      } else {
        // 完成注册
        await this.completeRegistration()
      }
    } catch (error) {
      wx.showToast({
        title: error.message || '处理失败',
        icon: 'none'
      })
    } finally {
      wx.hideLoading()
      this.setData({ processing: false })
    }
  },

  // 完成注册
  async completeRegistration() {
    try {
      // 调用后端API完成注册
      const res = await app.request({
        url: `${app.globalData.baseUrl}/voiceprint/register`,
        method: 'POST',
        data: {
          recordings: this.data.recordings
        }
      })

      if (res.success) {
        this.setData({
          currentStep: 3,
          registrationTime: this.formatTime(new Date())
        })
      } else {
        throw new Error(res.message || '注册失败')
      }
    } catch (error) {
      wx.showModal({
        title: '注册失败',
        content: error.message || '声纹注册失败，请重试',
        showCancel: false,
        confirmText: '确定'
      })
    }
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

  // 开始波形动画
  startWaveformAnimation() {
    this.setData({
      animationTimer: setInterval(() => {
        if (this.data.isRecording) {
          this.updateWaveformData()
        }
      }, 100)
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

  // 去验证页面
  goToVerify() {
    wx.redirectTo({
      url: '/pages/voiceprint/verify/verify'
    })
  },

  // 返回首页
  goHome() {
    wx.switchTab({
      url: '/pages/index/index'
    })
  },

  // 格式化时间
  formatTime(seconds) {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  },

  // 格式化日期时间
  formatDateTime(date) {
    const year = date.getFullYear()
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const day = date.getDate().toString().padStart(2, '0')
    const hour = date.getHours().toString().padStart(2, '0')
    const minute = date.getMinutes().toString().padStart(2, '0')
    return `${year}-${month}-${day} ${hour}:${minute}`
  }
})