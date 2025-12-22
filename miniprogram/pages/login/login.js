const app = getApp()

Page({
  data: {
    logging: false
  },

  onLoad() {
    // 检查是否已经登录
    if (app.globalData.userInfo) {
      // 如果已登录，直接跳转到首页
      this.redirectToHome()
    }
  },

  onShow() {
    // 每次显示时检查登录状态
    if (app.globalData.userInfo) {
      this.redirectToHome()
    }
  },

  // 微信登录
  async wxLogin() {
    if (this.data.logging) return

    this.setData({ logging: true })

    try {
      // 获取微信登录码
      const loginRes = await this.getWxLoginCode()
      
      // 获取用户信息
      const userProfile = await this.getUserProfile()
      
      // 发送到后端验证
      await this.sendToBackend(loginRes.code, userProfile.userInfo)
      
      // 登录成功，跳转到首页
      this.redirectToHome()
      
    } catch (error) {
      console.error('登录失败:', error)
      
      wx.showModal({
        title: '登录失败',
        content: error.message || '登录过程中出现错误，请重试',
        showCancel: false,
        confirmText: '确定'
      })
    } finally {
      this.setData({ logging: false })
    }
  },

  // 获取微信登录码
  getWxLoginCode() {
    return new Promise((resolve, reject) => {
      wx.login({
        success: (res) => {
          if (res.code) {
            resolve(res)
          } else {
            reject(new Error('获取微信登录码失败'))
          }
        },
        fail: (err) => {
          reject(new Error('微信登录接口调用失败: ' + err.errMsg))
        }
      })
    })
  },

  // 获取用户信息
  getUserProfile() {
    return new Promise((resolve, reject) => {
      wx.getUserProfile({
        desc: '用于完善用户资料',
        success: (res) => {
          resolve(res)
        },
        fail: (err) => {
          // 如果用户拒绝，给一个更友好的提示
          if (err.errMsg.includes('cancel')) {
            reject(new Error('需要授权用户信息才能使用'))
          } else {
            reject(new Error('获取用户信息失败: ' + err.errMsg))
          }
        }
      })
    })
  },

  // 发送数据到后端
  async sendToBackend(code, userInfo) {
    try {
      const res = await app.request({
        url: `${app.globalData.baseUrl}/auth/wx-login`,
        method: 'POST',
        data: {
          code: code,
          userInfo: userInfo
        },
        header: {
          'Content-Type': 'application/json'
        }
      })

      if (res.success) {
        const { token, userInfo: backendUserInfo } = res.data
        
        // 保存到全局数据
        app.globalData.token = token
        app.globalData.userInfo = backendUserInfo
        
        // 保存到本地存储
        wx.setStorageSync('token', token)
        wx.setStorageSync('userInfo', backendUserInfo)
        
        wx.showToast({
          title: '登录成功',
          icon: 'success',
          duration: 1500
        })
        
      } else {
        throw new Error(res.message || '后端验证失败')
      }
    } catch (error) {
      // 如果是网络错误或服务器错误，给出更具体的提示
      if (error.message.includes('request:fail')) {
        throw new Error('网络连接失败，请检查网络设置')
      } else if (error.message.includes('timeout')) {
        throw new Error('请求超时，请重试')
      } else {
        throw error
      }
    }
  },

  // 跳转到首页
  redirectToHome() {
    wx.switchTab({
      url: '/pages/index/index',
      fail: (err) => {
        console.error('跳转首页失败:', err)
        // 如果switchTab失败，尝试使用reLaunch
        wx.reLaunch({
          url: '/pages/index/index'
        })
      }
    })
  },

  // 显示用户协议
  showUserAgreement() {
    wx.showModal({
      title: '用户协议',
      content: '1. 本系统仅限企业内部员工使用\n2. 用户需提供真实身份信息\n3. 声纹信息将被加密存储\n4. 禁止分享账号给他人使用\n5. 如有问题请联系管理员',
      showCancel: false,
      confirmText: '我知道了'
    })
  },

  // 显示隐私政策
  showPrivacyPolicy() {
    wx.showModal({
      title: '隐私政策',
      content: '1. 我们承诺保护您的隐私安全\n2. 声纹信息采用加密存储\n3. 不会向第三方泄露个人信息\n4. 仅用于身份识别和会议记录\n5. 您有权随时删除个人数据',
      showCancel: false,
      confirmText: '我知道了'
    })
  },

  // 检查小程序更新
  checkForUpdate() {
    if (wx.canIUse('getUpdateManager')) {
      const updateManager = wx.getUpdateManager()
      
      updateManager.onCheckForUpdate((res) => {
        if (res.hasUpdate) {
          updateManager.onUpdateReady(() => {
            wx.showModal({
              title: '更新提示',
              content: '新版本已经准备好，是否重启应用？',
              success: (res) => {
                if (res.confirm) {
                  updateManager.applyUpdate()
                }
              }
            })
          })
          
          updateManager.onUpdateFailed(() => {
            wx.showModal({
              title: '更新失败',
              content: '新版本下载失败，请检查网络后重试',
              showCancel: false
            })
          })
        }
      })
    }
  }
})