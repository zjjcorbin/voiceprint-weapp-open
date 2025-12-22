const app = getApp()

Page({
  data: {
    userInfo: {},
    voiceprintStatus: {
      registered: false,
      sampleCount: 0,
      accuracy: 0,
      registrationTime: null
    },
    verificationStats: {
      totalCount: 0,
      recentCount: 0,
      successCount: 0,
      failureCount: 0
    },
    verificationHistory: [],
    showEditModal: false,
    editForm: {
      name: '',
      department: '',
      employeeId: ''
    },
    saving: false
  },

  onLoad() {
    this.loadUserInfo()
    this.loadVoiceprintStatus()
    this.loadVerificationStats()
    this.loadVerificationHistory()
  },

  onShow() {
    // 每次显示时刷新数据
    this.loadUserInfo()
    this.loadVoiceprintStatus()
    this.loadVerificationStats()
  },

  // 加载用户信息
  loadUserInfo() {
    const userInfo = app.globalData.userInfo || {}
    this.setData({
      userInfo: userInfo,
      editForm: {
        name: userInfo.name || '',
        department: userInfo.department || '',
        employeeId: userInfo.employeeId || ''
      }
    })
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
            accuracy: res.data.accuracy || 0,
            registrationTime: res.data.registrationTime
          }
        })
      }
    } catch (error) {
      console.error('加载声纹状态失败:', error)
    }
  },

  // 加载验证统计
  async loadVerificationStats() {
    try {
      const res = await app.request({
        url: `${app.globalData.baseUrl}/voiceprint/stats`,
        method: 'GET'
      })

      if (res.success) {
        this.setData({
          verificationStats: {
            totalCount: res.data.totalCount || 0,
            recentCount: res.data.recentCount || 0,
            successCount: res.data.successCount || 0,
            failureCount: res.data.failureCount || 0
          }
        })
      }
    } catch (error) {
      console.error('加载验证统计失败:', error)
    }
  },

  // 加载验证历史
  async loadVerificationHistory() {
    try {
      const res = await app.request({
        url: `${app.globalData.baseUrl}/voiceprint/history`,
        method: 'GET',
        data: {
          limit: 5
        }
      })

      if (res.success) {
        this.setData({
          verificationHistory: res.data.map(item => ({
            ...item,
            createdAt: new Date(item.createdAt)
          }))
        })
      }
    } catch (error) {
      console.error('加载验证历史失败:', error)
    }
  },

  // 跳转到声纹注册
  goToRegister() {
    wx.navigateTo({
      url: '/pages/voiceprint/register/register'
    })
  },

  // 跳转到声纹验证
  goToVerify() {
    if (!this.data.voiceprintStatus.registered) {
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

    wx.navigateTo({
      url: '/pages/voiceprint/verify/verify'
    })
  },

  // 重新注册声纹
  reRegister() {
    wx.showModal({
      title: '重新注册',
      content: '重新注册将覆盖您当前的声纹信息，确定继续吗？',
      confirmText: '确定',
      confirmColor: '#ff3b30',
      success: (res) => {
        if (res.confirm) {
          wx.navigateTo({
            url: '/pages/voiceprint/register/register?reRegister=true'
          })
        }
      }
    })
  },

  // 查看验证历史
  viewVerificationHistory() {
    wx.navigateTo({
      url: '/pages/history/history'
    })
  },

  // 查看准确率统计
  viewAccuracyStats() {
    wx.navigateTo({
      url: '/pages/stats/stats'
    })
  },

  // 编辑资料
  editProfile() {
    this.setData({
      showEditModal: true
    })
  },

  // 关闭编辑弹窗
  closeEditModal() {
    this.setData({
      showEditModal: false
    })
  },

  // 姓名输入
  onNameInput(e) {
    this.setData({
      'editForm.name': e.detail.value
    })
  },

  // 部门输入
  onDepartmentInput(e) {
    this.setData({
      'editForm.department': e.detail.value
    })
  },

  // 工号输入
  onEmployeeIdInput(e) {
    this.setData({
      'editForm.employeeId': e.detail.value
    })
  },

  // 保存资料
  async saveProfile() {
    if (this.data.saving) return

    const { name, department, employeeId } = this.data.editForm

    if (!name.trim()) {
      wx.showToast({
        title: '请输入姓名',
        icon: 'none'
      })
      return
    }

    this.setData({ saving: true })

    try {
      const res = await app.request({
        url: `${app.globalData.baseUrl}/user/profile`,
        method: 'PUT',
        data: {
          name: name.trim(),
          department: department.trim(),
          employeeId: employeeId.trim()
        }
      })

      if (res.success) {
        // 更新全局用户信息
        const updatedUserInfo = {
          ...app.globalData.userInfo,
          name: name.trim(),
          department: department.trim(),
          employeeId: employeeId.trim()
        }

        app.globalData.userInfo = updatedUserInfo
        wx.setStorageSync('userInfo', updatedUserInfo)

        this.setData({
          userInfo: updatedUserInfo,
          showEditModal: false
        })

        wx.showToast({
          title: '保存成功',
          icon: 'success'
        })
      } else {
        throw new Error(res.message || '保存失败')
      }
    } catch (error) {
      wx.showToast({
        title: error.message || '保存失败',
        icon: 'none'
      })
    } finally {
      this.setData({ saving: false })
    }
  },

  // 查看隐私政策
  viewPrivacyPolicy() {
    wx.showModal({
      title: '隐私政策',
      content: '1. 我们承诺保护您的隐私安全\n2. 声纹信息采用加密存储\n3. 不会向第三方泄露个人信息\n4. 仅用于身份识别和会议记录\n5. 您有权随时删除个人数据\n\n详细政策请访问企业内网查看完整版隐私政策。',
      showCancel: false,
      confirmText: '我知道了'
    })
  },

  // 联系支持
  contactSupport() {
    wx.showActionSheet({
      itemList: ['电话支持', '邮件支持', '在线客服'],
      success: (res) => {
        switch (res.tapIndex) {
          case 0: // 电话支持
            wx.makePhoneCall({
              phoneNumber: '400-123-4567'
            })
            break
          case 1: // 邮件支持
            wx.setClipboardData({
              data: 'support@company.com',
              success: () => {
                wx.showToast({
                  title: '邮箱已复制',
                  icon: 'success'
                })
              }
            })
            break
          case 2: // 在线客服
            wx.showToast({
              title: '正在连接客服...',
              icon: 'loading',
              duration: 2000
            })
            break
        }
      }
    })
  },

  // 查看历史详情
  viewHistoryDetail(e) {
    const historyId = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/history/detail/detail?id=${historyId}`
    })
  },

  // 查看全部历史
  viewAllHistory() {
    wx.navigateTo({
      url: '/pages/history/history'
    })
  },

  // 退出登录
  logout() {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出登录吗？',
      confirmText: '确定',
      confirmColor: '#ff3b30',
      success: (res) => {
        if (res.confirm) {
          app.logout()
        }
      }
    })
  },

  // 格式化日期
  formatDate(timestamp) {
    if (!timestamp) return '未知'
    const date = new Date(timestamp)
    const year = date.getFullYear()
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const day = date.getDate().toString().padStart(2, '0')
    return `${year}-${month}-${day}`
  },

  // 格式化日期时间
  formatDateTime(date) {
    const now = new Date()
    const diff = now - date
    
    if (diff < 60000) {
      return '刚刚'
    } else if (diff < 3600000) {
      return Math.floor(diff / 60000) + '分钟前'
    } else if (diff < 86400000) {
      return Math.floor(diff / 3600000) + '小时前'
    } else if (diff < 604800000) {
      return Math.floor(diff / 86400000) + '天前'
    } else {
      const year = date.getFullYear()
      const month = (date.getMonth() + 1).toString().padStart(2, '0')
      const day = date.getDate().toString().padStart(2, '0')
      const hour = date.getHours().toString().padStart(2, '0')
      const minute = date.getMinutes().toString().padStart(2, '0')
      return `${month}-${day} ${hour}:${minute}`
    }
  }
})