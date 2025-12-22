const app = getApp()

Page({
  data: {
    meetings: [],
    loading: false,
    hasMore: true,
    page: 1,
    pageSize: 10,
    searchKeyword: '',
    filterStatus: 'all', // all, ongoing, completed, scheduled
    activeTab: 0,
    tabs: ['全部', '进行中', '已完成', '已安排']
  },

  onLoad() {
    this.loadMeetings()
  },

  onShow() {
    // 每次显示时刷新数据
    this.refreshMeetings()
  },

  onPullDownRefresh() {
    this.refreshMeetings()
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.loadMoreMeetings()
    }
  },

  // 刷新会议列表
  async refreshMeetings() {
    this.setData({
      page: 1,
      hasMore: true,
      meetings: []
    })
    await this.loadMeetings()
    wx.stopPullDownRefresh()
  },

  // 加载会议列表
  async loadMeetings() {
    if (this.data.loading) return

    this.setData({ loading: true })

    try {
      const params = {
        page: this.data.page,
        pageSize: this.data.pageSize,
        status: this.getStatusFilter()
      }

      if (this.data.searchKeyword) {
        params.keyword = this.data.searchKeyword
      }

      const res = await app.request({
        url: `${app.globalData.baseUrl}/meetings`,
        method: 'GET',
        data: params
      })

      if (res.success) {
        const newMeetings = res.data.meetings.map(meeting => ({
          ...meeting,
          startTime: this.formatDateTime(meeting.startTime),
          endTime: this.formatDateTime(meeting.endTime),
          createdAt: this.formatTime(meeting.createdAt)
        }))

        const meetings = this.data.page === 1 ? newMeetings : [...this.data.meetings, ...newMeetings]

        this.setData({
          meetings: meetings,
          hasMore: newMeetings.length >= this.data.pageSize,
          loading: false
        })
      }
    } catch (error) {
      console.error('加载会议列表失败:', error)
      this.setData({ loading: false })
      wx.showToast({
        title: error.message || '加载失败',
        icon: 'none'
      })
    }
  },

  // 加载更多会议
  loadMoreMeetings() {
    this.setData({
      page: this.data.page + 1
    })
    this.loadMeetings()
  },

  // 切换标签
  switchTab(e) {
    const index = e.currentTarget.dataset.index
    this.setData({
      activeTab: index,
      filterStatus: this.getStatusByTab(index)
    })
    this.refreshMeetings()
  },

  // 根据标签获取状态
  getStatusByTab(index) {
    const statusMap = ['all', 'ongoing', 'completed', 'scheduled']
    return statusMap[index]
  },

  // 根据标签获取筛选状态
  getStatusFilter() {
    return this.data.filterStatus === 'all' ? undefined : this.data.filterStatus
  },

  // 搜索输入
  onSearchInput(e) {
    this.setData({
      searchKeyword: e.detail.value
    })
  },

  // 搜索
  onSearch() {
    this.refreshMeetings()
  },

  // 清除搜索
  onClearSearch() {
    this.setData({
      searchKeyword: ''
    })
    this.refreshMeetings()
  },

  // 创建会议
  createMeeting() {
    wx.navigateTo({
      url: '/pages/meeting/create/create'
    })
  },

  // 查看会议详情
  viewMeeting(e) {
    const meetingId = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/meeting/detail/detail?id=${meetingId}`
    })
  },

  // 开始会议录音
  async startRecording(e) {
    const meetingId = e.currentTarget.dataset.id
    const meeting = this.data.meetings.find(m => m.id === meetingId)
    
    if (!meeting) return

    wx.showModal({
      title: '开始会议录音',
      content: `确定要开始会议"${meeting.title}"的录音吗？`,
      success: async (res) => {
        if (res.confirm) {
          await this.doStartRecording(meetingId)
        }
      }
    })
  },

  // 执行开始录音
  async doStartRecording(meetingId) {
    wx.showLoading({
      title: '正在启动录音...',
      mask: true
    })

    try {
      const res = await app.request({
        url: `${app.globalData.baseUrl}/meetings/${meetingId}/start-recording`,
        method: 'POST'
      })

      wx.hideLoading()

      if (res.success) {
        wx.showToast({
          title: '录音已启动',
          icon: 'success'
        })
        
        // 刷新会议状态
        this.refreshMeetings()
        
        // 跳转到会议详情页面
        wx.navigateTo({
          url: `/pages/meeting/detail/detail?id=${meetingId}&recording=true`
        })
      } else {
        throw new Error(res.message || '启动录音失败')
      }
    } catch (error) {
      wx.hideLoading()
      wx.showToast({
        title: error.message || '启动录音失败',
        icon: 'none'
      })
    }
  },

  // 停止会议录音
  async stopRecording(e) {
    const meetingId = e.currentTarget.dataset.id
    const meeting = this.data.meetings.find(m => m.id === meetingId)
    
    if (!meeting) return

    wx.showModal({
      title: '停止会议录音',
      content: `确定要停止会议"${meeting.title}"的录音吗？`,
      success: async (res) => {
        if (res.confirm) {
          await this.doStopRecording(meetingId)
        }
      }
    })
  },

  // 执行停止录音
  async doStopRecording(meetingId) {
    wx.showLoading({
      title: '正在停止录音...',
      mask: true
    })

    try {
      const res = await app.request({
        url: `${app.globalData.baseUrl}/meetings/${meetingId}/stop-recording`,
        method: 'POST'
      })

      wx.hideLoading()

      if (res.success) {
        wx.showToast({
          title: '录音已停止',
          icon: 'success'
        })
        
        // 刷新会议状态
        this.refreshMeetings()
      } else {
        throw new Error(res.message || '停止录音失败')
      }
    } catch (error) {
      wx.hideLoading()
      wx.showToast({
        title: error.message || '停止录音失败',
        icon: 'none'
      })
    }
  },

  // 删除会议
  deleteMeeting(e) {
    const meetingId = e.currentTarget.dataset.id
    const meeting = this.data.meetings.find(m => m.id === meetingId)
    
    if (!meeting) return

    wx.showModal({
      title: '删除会议',
      content: `确定要删除会议"${meeting.title}"吗？此操作不可恢复。`,
      confirmText: '删除',
      confirmColor: '#ff4757',
      success: async (res) => {
        if (res.confirm) {
          await this.doDeleteMeeting(meetingId)
        }
      }
    })
  },

  // 执行删除会议
  async doDeleteMeeting(meetingId) {
    wx.showLoading({
      title: '正在删除...',
      mask: true
    })

    try {
      const res = await app.request({
        url: `${app.globalData.baseUrl}/meetings/${meetingId}`,
        method: 'DELETE'
      })

      wx.hideLoading()

      if (res.success) {
        wx.showToast({
          title: '删除成功',
          icon: 'success'
        })
        
        // 刷新会议列表
        this.refreshMeetings()
      } else {
        throw new Error(res.message || '删除失败')
      }
    } catch (error) {
      wx.hideLoading()
      wx.showToast({
        title: error.message || '删除失败',
        icon: 'none'
      })
    }
  },

  // 获取状态样式
  getStatusClass(status) {
    const statusMap = {
      'scheduled': 'scheduled',
      'ongoing': 'ongoing',
      'completed': 'completed',
      'cancelled': 'cancelled'
    }
    return statusMap[status] || ''
  },

  // 获取状态文本
  getStatusText(status) {
    const statusMap = {
      'scheduled': '已安排',
      'ongoing': '进行中',
      'completed': '已完成',
      'cancelled': '已取消'
    }
    return statusMap[status] || status
  },

  // 格式化时间
  formatTime(timestamp) {
    const now = new Date()
    const time = new Date(timestamp)
    const diff = now - time
    
    if (diff < 60000) {
      return '刚刚'
    } else if (diff < 3600000) {
      return Math.floor(diff / 60000) + '分钟前'
    } else if (diff < 86400000) {
      return Math.floor(diff / 3600000) + '小时前'
    } else if (diff < 604800000) {
      return Math.floor(diff / 86400000) + '天前'
    } else {
      return time.toLocaleDateString()
    }
  },

  // 格式化日期时间
  formatDateTime(timestamp) {
    const date = new Date(timestamp)
    const year = date.getFullYear()
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const day = date.getDate().toString().padStart(2, '0')
    const hour = date.getHours().toString().padStart(2, '0')
    const minute = date.getMinutes().toString().padStart(2, '0')
    return `${year}-${month}-${day} ${hour}:${minute}`
  }
})