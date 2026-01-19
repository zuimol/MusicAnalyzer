"""
MusicAnalyzer UI 组件库
提供可复用的 UI 组件和 HTML/JavaScript 功能
"""

import streamlit as st


def copy_button_html(text: str, button_id: str) -> str:
    """
    生成可复制的按钮 HTML
    
    Args:
        text: 要复制的文本
        button_id: 按钮唯一ID
    
    Returns:
        HTML 字符串
    """
    # 转义单引号以避免 JavaScript 语法错误
    escaped_text = text.replace("'", "\\'")
    
    return f"""
    <button onclick="
        const text = '{escaped_text}';
        navigator.clipboard.writeText(text).then(() => {{
            alert('✅ 已复制: ' + text);
        }}).catch(err => {{
            console.error('复制失败:', err);
        }});
    " style="
        padding: 5px 10px;
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-weight: 500;
        transition: background-color 0.3s;
    " onmouseover="this.style.backgroundColor='#45a049';" onmouseout="this.style.backgroundColor='#4CAF50';">
    📋 复制
    </button>
    """


def copy_icon_button_html(text: str, button_id: str) -> str:
    """
    生成图标按钮 HTML（仅图标，用于表格行）
    
    Args:
        text: 要复制的文本
        button_id: 按钮唯一ID
    
    Returns:
        HTML 字符串
    """
    # 转义单引号
    escaped_text = text.replace("'", "\\'")
    
    return f"""
    <button onclick="
        const text = '{escaped_text}';
        navigator.clipboard.writeText(text).then(() => {{
            alert('✅ 已复制: ' + text);
        }}).catch(err => {{
            console.error('复制失败:', err);
        }});
    " style="
        padding: 5px 8px;
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 12px;
        transition: background-color 0.3s;
    " onmouseover="this.style.backgroundColor='#45a049';" onmouseout="this.style.backgroundColor='#4CAF50';">
    📋
    </button>
    """


def render_copy_button(text: str, button_key: str):
    """
    在 Streamlit 中渲染可复制的按钮
    
    Args:
        text: 要复制的文本
        button_key: 按钮唯一标识
    """
    html = copy_button_html(text, button_key)
    st.markdown(html, unsafe_allow_html=True)


def render_copy_icon_button(text: str, button_key: str):
    """
    在 Streamlit 中渲染可复制的图标按钮
    
    Args:
        text: 要复制的文本
        button_key: 按钮唯一标识
    """
    html = copy_icon_button_html(text, button_key)
    st.markdown(html, unsafe_allow_html=True)


def metric_card(label: str, value, icon: str = ""):
    """
    渲染指标卡片
    
    Args:
        label: 标签
        value: 值
        icon: 图标
    """
    st.metric(f"{icon} {label}" if icon else label, value)


def section_header(title: str, divider_color: str = "blue"):
    """
    渲染章节标题
    
    Args:
        title: 标题文本
        divider_color: 分割线颜色
    """
    st.subheader(title, divider=divider_color)


def info_box(message: str, type_: str = "info"):
    """
    渲染信息框
    
    Args:
        message: 消息文本
        type_: 类型 ("info", "success", "warning", "error")
    """
    if type_ == "success":
        st.success(message)
    elif type_ == "warning":
        st.warning(message)
    elif type_ == "error":
        st.error(message)
    else:
        st.info(message)
