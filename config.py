"""
MusicAnalyzer 配置文件
集中管理常量、样式和配置
"""

# ========== 音乐格式配置 ==========
SUPPORTED_EXT = {".mp3", ".flac", ".wav", ".m4a", ".ogg", ".aiff", ".alac"}

# 格式优先级（高到低）
FORMAT_PRIORITY = {
    "flac": 5,
    "wav": 4,
    "alac": 4,
    "aiff": 3,
    "aac": 2,
    "mp3": 1,
}

# ========== 页面配置 ==========
PAGE_CONFIG = {
    "page_title": "🎵 音乐库分析",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# ========== 颜色和样式 ==========
COLORS = {
    "primary": "#667eea",
    "secondary": "#764ba2",
    "success": "#48bb78",
    "danger": "#f56565",
    "warning": "#ed8936",
    "info": "#4299e1",
}

# ========== 页面样式 CSS ==========
STYLE_CSS = """
<style>
    /* 全局色彩主题 */
    :root {
        --primary: #667eea;
        --secondary: #764ba2;
        --success: #48bb78;
        --danger: #f56565;
        --warning: #ed8936;
        --info: #4299e1;
    }
    
    /* 减少全局间距 */
    .main {
        padding-top: 1rem !important;
        padding-bottom: 0 !important;
    }
    
    /* 标题统一风格 */
    h1, h2, h3, h4, h5, h6 {
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    h1 { font-size: 2.2rem; }
    h2 { font-size: 1.6rem; }
    
    /* 卡片风格 */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    
    /* 路径显示 */
    .path-display {
        background: linear-gradient(135deg, #f0f2f6 0%, #e2e8f0 100%);
        padding: 12px 16px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        font-family: 'Courier New', monospace;
        font-size: 14px;
        margin: 4px 0 !important;
    }
    
    /* 按钮容器对齐 */
    .button-row {
        display: flex;
        gap: 8px;
        align-items: center;
        justify-content: space-between;
    }
    
    /* 警告框 */
    .stAlert {
        border-radius: 8px;
        margin: 4px 0 !important;
        padding: 8px 12px !important;
    }
    
    /* 结果区域占用高度 */
    .stDataFrame {
        min-height: 200px;
    }
</style>
"""

# ========== 分页配置 ==========
PAGINATION = {
    "duplicates_per_page": 5,
    "mp3_per_page": 20,
}

# ========== 应用信息 ==========
APP_INFO = {
    "name": "🎵 音乐库智能分析工具",
    "version": "1.0.0",
    "description": "智能识别和清理音乐库中的重复歌曲、低质MP3文件",
}
