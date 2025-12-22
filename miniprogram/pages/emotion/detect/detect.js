// pages/emotion/detect/detect.js
const app = getApp()

Page({
  data: {
    // 录音状态
    isRecording: false,
    recordingTime: 0,
    audioUrl: '',
    audioDuration: 0,
    isPlaying: false,
    
    // 检测状态
    detecting: false,
    loadingText: '正在上传音频...',
    
    // 结果数据
    emotionResult: null,
    
    // 历史记录
    historyRecords: [],
    
    // 录音管理器
    recorderManager: null,
    recordingTimer: null,
    
    // 情绪配置
    emotionConfig: {
      neutral: { name: '中性', emoji: '😐', color: '#95a5a6' },
      happy: { name: '开心', emoji: '😊', color: '#f39c12' },
      sad: { name: '悲伤', emoji: '😢', color: '#3498db' },
      angry: { name: '愤怒', emoji: '😠', color: '#e74c3c' },
      fear: { name: '恐惧', emoji: '😨', color: '#9b59b6' },
      disgust: { name: '厌恶', emoji: '😒', color: '#27ae60' },
      surprise: { name: '惊讶', emoji: '😲', color: '#e67e22' }
    }
  },

  onLoad(options) {
    this.initRecorderManager()
    this.loadHistoryRecords()
  },

  onShow() {
    // 页面显示时刷新历史记录
    this.loadHistoryRecords()
  },

  // 初始化录音管理器
  initRecorderManager() {
    const recorderManager = wx.getRecorderManager()
    
    recorderManager.onStart(() => {
      console.log('录音开始')
      this.setData({ 
        isRecording: true,
        recordingTime: 0 
      })
      this.startRecordingTimer()
    })

    recorderManager.onStop((res) => {
      console.log('录音结束', res)
      this.setData({ 
        isRecording: false,
        audioUrl: res.tempFilePath,
        audioDuration: Math.round(res.duration / 1000)
      })
      this.stopRecordingTimer()
    })

    recorderManager.onError((err) => {
      console.error('录音错误', err)
      wx.showToast({
        title: '录音失败',
        icon: 'none'
      })
      this.setData({ isRecording: false })
      this.stopRecordingTimer()
    })

    this.setData({ recorderManager })
  },

  // 开始录音
  startRecording() {
    if (this.data.isRecording) return

    // 检查录音权限
    wx.getSetting({
      success: (res) => {
        if (!res.authSetting['scope.record']) {
          wx.authorize({
            scope: 'scope.record',
            success: () => {
              this.doStartRecording()
            },
            fail: () => {
              wx.showModal({
                title: '提示',
                content: '需要录音权限才能使用此功能',
                confirmText: '去设置',
                success: (modalRes) => {
                  if (modalRes.confirm) {
                    wx.openSetting()
                  }
                }
              })
            }
          })
        } else {
          this.doStartRecording()
        }
      }
    })
  },

  doStartRecording() {
    this.data.recorderManager.start({
      format: 'wav',
      sampleRate: 16000,
      numberOfChannels: 1,
      encodeBitRate: 96000,
      frameSize: 50
    })
  },

  // 停止录音
  stopRecording() {
    if (!this.data.isRecording) return
    this.data.recorderManager.stop()
  },

  // 开始录音计时
  startRecordingTimer() {
    let time = 0
    this.data.recordingTimer = setInterval(() => {
      time++
      this.setData({ recordingTime: time })
      
      // 最长录音60秒
      if (time >= 60) {
        this.stopRecording()
      }
    }, 1000)
  },

  // 停止录音计时
  stopRecordingTimer() {
    if (this.data.recordingTimer) {
      clearInterval(this.data.recordingTimer)
      this.setData({ recordingTimer: null })
    }
  },

  // 播放/暂停音频
  togglePlay() {
    if (this.data.isPlaying) {
      wx.pauseBackgroundAudio()
    } else {
      wx.playBackgroundAudio({
        dataUrl: this.data.audioUrl,
        title: '录音音频'
      })
    }
    this.setData({ isPlaying: !this.data.isPlaying })
  },

  // 音频播放事件
  onAudioPlay() {
    this.setData({ isPlaying: true })
  },

  onAudioPause() {
    this.setData({ isPlaying: false })
  },

  onAudioEnded() {
    this.setData({ isPlaying: false })
  },

  onTimeUpdate(e) {
    // 可以在这里更新播放进度
  },

  // 检测情绪
  async detectEmotion() {
    if (!this.data.audioUrl) {
      wx.showToast({
        title: '请先录音',
        icon: 'none'
      })
      return
    }

    this.setData({ 
      detecting: true,
      loadingText: '正在上传音频...'
    })

    try {
      // 上传音频文件
      this.setData({ loadingText: '正在分析情绪...' })
      
      const result = await app.request({
        url: '/api/emotion/detect',
        method: 'POST',
        data: {
          audio_file: this.data.audioUrl,
          employee_id: wx.getStorageSync('employee_id'),
          require_analysis: true
        }
      })

      if (result.success && result.emotion_feature) {
        const emotionFeature = result.emotion_feature
        
        // 格式化情绪概率数据
        const emotionProbabilities = Object.entries(emotionFeature.emotion_probabilities)
          .map(([emotion, probability]) => ({ emotion, probability }))
          .sort((a, b) => b.probability - a.probability)

        this.setData({
          emotionResult: {
            ...emotionFeature,
            confidence: Math.round(emotionFeature.confidence * 100),
            emotion_probabilities: emotionProbabilities,
            intensity: emotionFeature.intensity,
            complexity: emotionFeature.complexity,
            quality_score: emotionFeature.quality_score,
            analysis: emotionFeature.analysis || {}
          }
        })

        wx.showToast({
          title: '情绪检测完成',
          icon: 'success'
        })
      } else {
        throw new Error(result.message || '检测失败')
      }

    } catch (error) {
      console.error('情绪检测失败:', error)
      wx.showToast({
        title: error.message || '情绪检测失败',
        icon: 'none'
      })
    } finally {
      this.setData({ detecting: false })
    }
  },

  // 重置检测
  resetDetection() {
    this.setData({
      audioUrl: '',
      audioDuration: 0,
      isPlaying: false,
      emotionResult: null
    })
  },

  // 保存结果
  async saveResult() {
    if (!this.data.emotionResult) return

    try {
      const result = await app.request({
        url: '/api/emotion/save',
        method: 'POST',
        data: {
          emotion_data: this.data.emotionResult,
          employee_id: wx.getStorageSync('employee_id')
        }
      })

      if (result.success) {
        wx.showToast({
          title: '保存成功',
          icon: 'success'
        })
        this.loadHistoryRecords()
      } else {
        throw new Error(result.message || '保存失败')
      }

    } catch (error) {
      console.error('保存结果失败:', error)
      wx.showToast({
        title: '保存失败',
        icon: 'none'
      })
    }
  },

  // 加载历史记录
  async loadHistoryRecords() {
    try {
      const result = await app.request({
        url: '/api/emotion/history/' + (wx.getStorageSync('employee_id') || 0),
        method: 'GET',
        data: { limit: 5 }
      })

      if (result && result.history) {
        this.setData({ 
          historyRecords: result.history.map(item => ({
            ...item,
            created_at: this.formatTime(item.created_at)
          }))
        })
      }
    } catch (error) {
      console.error('加载历史记录失败:', error)
    }
  },

  // 跳转到历史记录页面
  goToHistory() {
    wx.navigateTo({
      url: '/pages/emotion/history/history'
    })
  },

  // 跳转到详情页面
  goToDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/emotion/detail/detail?id=${id}`
    })
  },

  // 格式化时间
  formatTime(timeStr) {
    const date = new Date(timeStr)
    const now = new Date()
    const diff = now - date
    
    if (diff < 60000) {
      return '刚刚'
    } else if (diff < 3600000) {
      return `${Math.floor(diff / 60000)}分钟前`
    } else if (diff < 86400000) {
      return `${Math.floor(diff / 3600000)}小时前`
    } else if (diff < 604800000) {
      return `${Math.floor(diff / 86400000)}天前`
    } else {
      return date.toLocaleDateString()
    }
  },

  // 获取情绪表情
  getEmotionEmoji(emotion) {
    return this.data.emotionConfig[emotion]?.emoji || '😐'
  },

  // 获取情绪中文名
  getEmotionNameCN(emotion) {
    return this.data.emotionConfig[emotion]?.name || emotion
  },

  // 获取强度等级
  getIntensityLevel(intensity) {
    if (intensity >= 0.7) return 'high'
    if (intensity >= 0.5) return 'medium'
    return 'low'
  },

  // 获取强度文本
  getIntensityText(intensity) {
    if (intensity >= 0.7) return '强烈'
    if (intensity >= 0.5) return '中等'
    return '轻微'
  },

  // 获取复杂度等级
  getComplexityLevel(complexity) {
    if (complexity >= 0.7) return 'high'
    if (complexity >= 0.5) return 'medium'
    return 'low'
  },

  // 获取复杂度文本
  getComplexityText(complexity) {
    if (complexity >= 0.7) return '复杂'
    if (complexity >= 0.5) return '较复杂'
    return '简单'
  },

  // 获取质量等级
  getQualityLevel(quality) {
    if (quality >= 0.8) return 'high'
    if (quality >= 0.6) return 'medium'
    return 'low'
  },

  // 获取质量文本
  getQualityText(quality) {
    if (quality >= 0.8) return '优秀'
    if (quality >= 0.6) return '良好'
    return '一般'
  }
})