-- 声纹识别系统数据库结构

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    openid VARCHAR(100) UNIQUE,
    unionid VARCHAR(100),
    session_key VARCHAR(100),
    nickname VARCHAR(100),
    avatar_url TEXT,
    real_name VARCHAR(100),
    last_login_at TIMESTAMP NULL,
    login_count INT DEFAULT 0,
    preferences TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_openid (openid),
    INDEX idx_email (email)
);

-- 员工表
CREATE TABLE IF NOT EXISTS employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    department VARCHAR(100),
    position VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    voiceprint_registered BOOLEAN DEFAULT FALSE,
    voiceprint_count INT DEFAULT 0,
    avatar_url TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_employee_code (employee_code),
    INDEX idx_email (email)
);

-- 声纹表
CREATE TABLE IF NOT EXISTS voiceprints (
    voiceprint_id VARCHAR(64) PRIMARY KEY,
    employee_id INT NOT NULL,
    audio_sample_url TEXT NOT NULL,
    sample_duration FLOAT NOT NULL,
    sample_rate INT NOT NULL,
    feature_data JSON NOT NULL,
    feature_model VARCHAR(200) NOT NULL,
    embedding_version VARCHAR(50),
    quality_score FLOAT NOT NULL,
    clarity_score FLOAT,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    device_info JSON,
    environment_info JSON,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    INDEX idx_employee_id (employee_id),
    INDEX idx_is_active (is_active),
    INDEX idx_created_at (created_at)
);

-- 情绪检测记录表
CREATE TABLE IF NOT EXISTS emotion_detections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    detection_id VARCHAR(64) UNIQUE NOT NULL,
    employee_id INT,
    meeting_id INT,
    dominant_emotion VARCHAR(50) NOT NULL,
    confidence_score FLOAT NOT NULL,
    emotion_probabilities JSON NOT NULL,
    intensity FLOAT NOT NULL,
    complexity FLOAT NOT NULL,
    audio_url TEXT,
    audio_duration FLOAT NOT NULL,
    audio_quality_score FLOAT NOT NULL,
    emotion_analysis JSON,
    model_name VARCHAR(200) NOT NULL,
    model_version VARCHAR(50),
    processing_time FLOAT NOT NULL,
    is_success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE SET NULL,
    INDEX idx_detection_id (detection_id),
    INDEX idx_employee_id (employee_id),
    INDEX idx_meeting_id (meeting_id),
    INDEX idx_dominant_emotion (dominant_emotion),
    INDEX idx_created_at (created_at)
);

-- 情绪反馈表
CREATE TABLE IF NOT EXISTS emotion_feedbacks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    detection_id VARCHAR(64) NOT NULL,
    user_emotion VARCHAR(50),
    accuracy_rating INT,
    comments TEXT,
    is_accurate BOOLEAN,
    emotion_discrepancy VARCHAR(50),
    improvement_suggestions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (detection_id) REFERENCES emotion_detections(detection_id) ON DELETE CASCADE,
    INDEX idx_detection_id (detection_id),
    INDEX idx_created_at (created_at)
);

-- 情绪汇总表
CREATE TABLE IF NOT EXISTS emotion_summaries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    summary_date VARCHAR(10) NOT NULL,
    summary_type VARCHAR(20) NOT NULL,
    employee_count INT DEFAULT 0,
    total_detections INT DEFAULT 0,
    successful_detections INT DEFAULT 0,
    emotion_distribution JSON NOT NULL,
    average_confidence FLOAT DEFAULT 0.0,
    average_intensity FLOAT DEFAULT 0.0,
    average_complexity FLOAT DEFAULT 0.0,
    quality_distribution JSON NOT NULL,
    model_performance JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_summary_date (summary_date),
    INDEX idx_summary_type (summary_type)
);

-- 情绪预警表
CREATE TABLE IF NOT EXISTS emotion_alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alert_id VARCHAR(64) UNIQUE NOT NULL,
    employee_id INT NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    emotion_state JSON NOT NULL,
    duration_minutes INT NOT NULL,
    threshold_exceeded JSON NOT NULL,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolution_method VARCHAR(100),
    resolution_notes TEXT,
    recommendations JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    INDEX idx_alert_id (alert_id),
    INDEX idx_employee_id (employee_id),
    INDEX idx_severity (severity),
    INDEX idx_is_resolved (is_resolved)
);

-- 情绪洞察表
CREATE TABLE IF NOT EXISTS emotion_insights (
    id INT AUTO_INCREMENT PRIMARY KEY,
    insight_id VARCHAR(64) UNIQUE NOT NULL,
    employee_id INT NOT NULL,
    analysis_period VARCHAR(50) NOT NULL,
    insight_type VARCHAR(50) NOT NULL,
    emotional_patterns JSON NOT NULL,
    mood_trend VARCHAR(50) NOT NULL,
    stability_score FLOAT NOT NULL,
    triggers JSON,
    recommendations JSON,
    stress_indicators JSON,
    wellness_score FLOAT,
    data_points_count INT NOT NULL,
    confidence_level FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    INDEX idx_insight_id (insight_id),
    INDEX idx_employee_id (employee_id),
    INDEX idx_insight_type (insight_type)
);

-- 情绪对比表
CREATE TABLE IF NOT EXISTS emotion_comparisons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    comparison_id VARCHAR(64) UNIQUE NOT NULL,
    employee_id INT NOT NULL,
    comparison_type VARCHAR(50) NOT NULL,
    comparison_period VARCHAR(50) NOT NULL,
    baseline_emotion JSON NOT NULL,
    current_emotion JSON NOT NULL,
    changes JSON NOT NULL,
    significant_changes JSON NOT NULL,
    change_magnitude FLOAT NOT NULL,
    trend_direction VARCHAR(20) NOT NULL,
    statistical_significance FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    INDEX idx_comparison_id (comparison_id),
    INDEX idx_employee_id (employee_id),
    INDEX idx_comparison_type (comparison_type)
);

-- 会议表
CREATE TABLE IF NOT EXISTS meetings (
    meeting_id INT AUTO_INCREMENT PRIMARY KEY,
    meeting_code VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    organizer_id INT NOT NULL,
    meeting_room VARCHAR(100),
    expected_duration INT NOT NULL,
    status VARCHAR(20) DEFAULT 'scheduled',
    is_active BOOLEAN DEFAULT TRUE,
    scheduled_start TIMESTAMP NOT NULL,
    scheduled_end TIMESTAMP NOT NULL,
    actual_start TIMESTAMP NULL,
    actual_end TIMESTAMP NULL,
    participants JSON,
    max_participants INT,
    require_voiceprint BOOLEAN DEFAULT TRUE,
    enable_emotion_detection BOOLEAN DEFAULT TRUE,
    recording_enabled BOOLEAN DEFAULT FALSE,
    meeting_password VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (organizer_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    INDEX idx_meeting_code (meeting_code),
    INDEX idx_organizer_id (organizer_id),
    INDEX idx_status (status),
    INDEX idx_scheduled_start (scheduled_start)
);

-- 识别日志表
CREATE TABLE IF NOT EXISTS recognition_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT,
    voiceprint_id VARCHAR(64),
    audio_url TEXT,
    audio_duration FLOAT,
    confidence_score FLOAT,
    threshold_used FLOAT,
    is_success BOOLEAN NOT NULL,
    top_candidates JSON,
    model_version VARCHAR(100),
    processing_time FLOAT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE SET NULL,
    FOREIGN KEY (voiceprint_id) REFERENCES voiceprints(voiceprint_id) ON DELETE SET NULL,
    INDEX idx_employee_id (employee_id),
    INDEX idx_voiceprint_id (voiceprint_id),
    INDEX idx_is_success (is_success),
    INDEX idx_created_at (created_at)
);

-- 创建外键约束
ALTER TABLE employees ADD CONSTRAINT fk_organized_meetings 
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id);

-- 初始化数据
INSERT INTO users (username, hashed_password, is_admin, is_active) 
VALUES ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBdXwtGyIUJVQW', TRUE, TRUE)
ON DUPLICATE KEY UPDATE username = username;

-- 创建默认的会议组织者
INSERT INTO employees (employee_code, name, department, position, is_admin, is_active)
VALUES ('ADMIN001', '系统管理员', '系统管理', '管理员', TRUE, TRUE)
ON DUPLICATE KEY UPDATE employee_code = employee_code;