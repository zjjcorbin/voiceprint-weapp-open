App({
  globalData: {
    baseUrl: 'http://localhost:8000/api', // 开发环境
    // baseUrl: 'https://your-domain.com/api', // 生产环境
    userInfo: null,
    token: null,
    recordingManager: null,
    innerAudioContext: null
  },

  onLaunch() {
    console.log('声纹识别小程序启动')
    
    // 初始化录音管理器
    this.initRecorder()
    
    // 检查登录状态
    this.checkLoginStatus()
    
    // 获取系统信息
    wx.getSystemInfo({
      success: (res) => {
        this.globalData.systemInfo = res
        console.log('系统信息:', res)
      }
    })
  },

  onShow() {
    console.log('小程序显示')
  },

  onHide() {
    console.log('小程序隐藏')
    // 停止录音
    if (this.globalData.recordingManager) {
      this.stopRecording()
    }
  },

  // 初始化录音管理器
  initRecorder() {
    const recorderManager = wx.getRecorderManager()
    
    // 录音开始
    recorderManager.onStart(() => {
      console.log('录音开始')
      this.globalData.isRecording = true
    })

    // 录音停止
    recorderManager.onStop((res) => {
      console.log('录音停止', res)
      this.globalData.isRecording = false
      this.globalData.lastRecording = res
    })

    // 录音错误
    recorderManager.onError((err) => {
      console.error('录音错误:', err)
      this.globalData.isRecording = false
      wx.showToast({
        title: '录音失败: ' + err.errMsg,
        icon: 'none',
        duration: 2000
      })
    })

    this.globalData.recordingManager = recorderManager
  },

  // 开始录音
  startRecording(options = {}) {
    const defaultOptions = {
      duration: 30000, // 最长30秒
      sampleRate: 16000,
      numberOfChannels: 1,
      encodeBitRate: 96000,
      format: 'mp3',
      frameSize: 50
    }

    const recordOptions = Object.assign(defaultOptions, options)

    return new Promise((resolve, reject) => {
      // 检查录音权限
      wx.getSetting({
        success: (res) => {
          if (!res.authSetting['scope.record']) {
            wx.authorize({
              scope: 'scope.record',
              success: () => {
                this.globalData.recordingManager.start(recordOptions)
                resolve()
              },
              fail: () => {
                wx.showModal({
                  title: '需要录音权限',
                  content: '请允许使用录音功能以使用声纹识别',
                  showCancel: false
                })
                reject(new Error('录音权限被拒绝'))
              }
            })
          } else {
            this.globalData.recordingManager.start(recordOptions)
            resolve()
          }
        },
        fail: reject
      })
    })
  },

  // 停止录音
  stopRecording() {
    if (this.globalData.recordingManager && this.globalData.isRecording) {
      this.globalData.recordingManager.stop()
    }
  },

  // 检查登录状态
  checkLoginStatus() {
    const token = wx.getStorageSync('token')
    const userInfo = wx.getStorageSync('userInfo')

    if (token && userInfo) {
      this.globalData.token = token
      this.globalData.userInfo = userInfo
      
      // 验证token有效性
      this.validateToken()
    }
  },

  // 验证token
  validateToken() {
    wx.request({
      url: `${this.globalData.baseUrl}/auth/validate`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${this.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode !== 200) {
          this.logout()
        }
      },
      fail: () => {
        this.logout()
      }
    })
  },

  // 微信登录
  wxLogin() {
    return new Promise((resolve, reject) => {
      wx.login({
        success: (loginRes) => {
          if (loginRes.code) {
            // 获取用户信息
            wx.getUserProfile({
              desc: '用于完善用户资料',
              success: (userRes) => {
                // 发送到后端
                wx.request({
                  url: `${this.globalData.baseUrl}/auth/wx-login`,
                  method: 'POST',
                  data: {
                    code: loginRes.code,
                    userInfo: userRes.userInfo
                  },
                  success: (res) => {
                    if (res.statusCode === 200) {
                      const { token, userInfo } = res.data.data
                      this.globalData.token = token
                      this.globalData.userInfo = userInfo
                      
                      // 存储到本地
                      wx.setStorageSync('token', token)
                      wx.setStorageSync('userInfo', userInfo)
                      
                      resolve(res.data.data)
                    } else {
                      reject(new Error(res.data.message || '登录失败'))
                    }
                  },
                  fail: reject
                })
              },
              fail: reject
            })
          } else {
            reject(new Error('获取微信登录码失败'))
          }
        },
        fail: reject
      })
    })
  },

  // 退出登录
  logout() {
    this.globalData.token = null
    this.globalData.userInfo = null
    wx.removeStorageSync('token')
    wx.removeStorageSync('userInfo')
    
    // 跳转到登录页
    wx.reLaunch({
      url: '/pages/login/login'
    })
  },

  // 封装网络请求
  request(options) {
    const defaultOptions = {
      header: {
        'Content-Type': 'application/json'
      },
      dataType: 'json'
    }

    // 添加认证头
    if (this.globalData.token) {
      defaultOptions.header['Authorization'] = `Bearer ${this.globalData.token}`
    }

    const requestOptions = Object.assign(defaultOptions, options)

    return new Promise((resolve, reject) => {
      wx.request({
        ...requestOptions,
        success: (res) => {
          if (res.statusCode === 401) {
            // token过期，重新登录
            this.logout()
            reject(new Error('登录已过期'))
          } else if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(res.data)
          } else {
            reject(new Error(res.data.message || '请求失败'))
          }
        },
        fail: (err) => {
          wx.showToast({
            title: '网络请求失败',
            icon: 'none'
          })
          reject(err)
        }
      })
    })
  },

  // 上传文件
  uploadFile(filePath, formData = {}) {
    return new Promise((resolve, reject) => {
      wx.uploadFile({
        url: `${this.globalData.baseUrl}/upload/audio`,
        filePath: filePath,
        name: 'audio',
        formData: formData,
        header: {
          'Authorization': this.globalData.token ? `Bearer ${this.globalData.token}` : ''
        },
        success: (res) => {
          try {
            const data = JSON.parse(res.data)
            if (res.statusCode >= 200 && res.statusCode < 300) {
              resolve(data)
            } else {
              reject(new Error(data.message || '上传失败'))
            }
          } catch (err) {
            reject(new Error('响应解析失败'))
          }
        },
        fail: reject
      })
    })
  }
})