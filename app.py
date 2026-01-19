import streamlit as st
import pandas as pd
import os
from pathlib import Path

from scanner import scan_music
from analyzer import analyze, find_duplicates, find_mp3_only, mark_files_to_delete, get_duplicates_to_delete
from config import PAGE_CONFIG, STYLE_CSS
from views import show_duplicates_view, show_mp3_view, show_dashboard

# 页面配置
st.set_page_config(**PAGE_CONFIG)

# 页面样式
st.markdown(STYLE_CSS, unsafe_allow_html=True)

# ========== 初始化会话状态 ==========
if "current_path" not in st.session_state:
    st.session_state.current_path = "G:\\music"
if "df" not in st.session_state:
    st.session_state.df = None
if "dup_page" not in st.session_state:
    st.session_state.dup_page = 0
if "mp3_page" not in st.session_state:
    st.session_state.mp3_page = 0
if "selected_function" not in st.session_state:
    st.session_state.selected_function = None

# ========== 工具函数 ==========
def delete_files(rows):
    """删除文件列表中的文件，并记录操作日志"""
    import datetime
    import json
    
    deleted = []
    failed = []
    log_entries = []
    
    # 创建 logs 目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 日志文件路径
    log_file = log_dir / f"delete_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    for file_path in rows["file_path"]:
        try:
            # 记录文件信息
            file_info = {
                "file_path": str(file_path),
                "file_name": Path(file_path).name,
                "timestamp": datetime.datetime.now().isoformat(),
                "status": "deleted",
                "error": None
            }
            
            # 执行删除
            os.remove(file_path)
            deleted.append(file_path)
            
            log_entries.append(file_info)
            print(f"✓ 已删除: {file_path}")
            
        except Exception as e:
            error_msg = str(e)
            failed.append((file_path, error_msg))
            
            # 记录失败信息
            file_info = {
                "file_path": str(file_path),
                "file_name": Path(file_path).name,
                "timestamp": datetime.datetime.now().isoformat(),
                "status": "failed",
                "error": error_msg
            }
            log_entries.append(file_info)
            print(f"✗ 删除失败: {file_path} - {error_msg}")
    
    # 写入日志文件
    if log_entries:
        log_data = {
            "operation": "delete_files",
            "timestamp": datetime.datetime.now().isoformat(),
            "summary": {
                "total": len(log_entries),
                "deleted": len(deleted),
                "failed": len(failed)
            },
            "entries": log_entries
        }
        
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
        print(f"\n📋 操作日志已保存: {log_file}")
    
    return deleted, failed

def get_subdirectories(path):
    """获取路径下的子目录列表"""
    try:
        return sorted([d.name for d in Path(path).iterdir() if d.is_dir() and not d.name.startswith(".")])
    except:
        return []

# ========== 标题和路径显示 ==========
st.title("🎵 音乐库智能分析工具")
st.markdown(f"<div class='path-display'>📂 当前路径: {st.session_state.current_path}</div>", unsafe_allow_html=True)

# ========== 左侧侧栏 ==========
with st.sidebar:
    st.markdown("### 🎛️ 扫描设置")
    
    # 路径输入
    new_path = st.text_input("📁 输入路径:", value=st.session_state.current_path, key="path_input")
    if new_path != st.session_state.current_path:
        st.session_state.current_path = new_path
        st.session_state.df = None
        st.session_state.selected_function = None
        st.rerun()
    
    st.divider()
    
    # 导航按钮
    col_up = st.columns(1)
    with col_up[0]:
        if st.button("⬆️ 上一级", use_container_width=True):
            parent = str(Path(st.session_state.current_path).parent)
            if parent != st.session_state.current_path:
                st.session_state.current_path = parent
                st.session_state.df = None
                st.session_state.selected_function = None
                st.rerun()
    
    # 子目录选择
    subdirs = get_subdirectories(st.session_state.current_path)
    if subdirs:
        st.markdown("**子目录快速跳转:**")
        for subdir in subdirs[:10]:  # 只显示前10个
            if st.button(f"📂 {subdir}", use_container_width=True, key=f"subdir_{subdir}"):
                new_path = str(Path(st.session_state.current_path) / subdir)
                st.session_state.current_path = new_path
                st.session_state.df = None
                st.session_state.selected_function = None
                st.rerun()
    
    st.divider()
    
    # 扫描按钮
    if st.button("🔍 开始扫描", use_container_width=True, type="primary"):
        if not Path(st.session_state.current_path).exists():
            st.error("❌ 路径不存在!")
        else:
            with st.spinner("正在扫描音乐文件..."):
                music_list = scan_music(st.session_state.current_path)
                if music_list:
                    st.session_state.df = pd.DataFrame(music_list)
                    st.session_state.df = analyze(st.session_state.df)
                    st.session_state.selected_function = None
                    st.success(f"✅ 扫描完成! 找到 {len(st.session_state.df)} 个文件")
                    st.rerun()
                else:
                    st.error("❌ 未找到音乐文件!")
    
    st.divider()
    
    # 功能选择按钮
    if st.session_state.df is not None:
        dup_count = find_duplicates(st.session_state.df)["song_key"].nunique() if len(find_duplicates(st.session_state.df)) > 0 else 0
        mp3_count = find_mp3_only(st.session_state.df)["song_key"].nunique() if len(find_mp3_only(st.session_state.df)) > 0 else 0
        
        st.markdown("### 🎯 分析功能")
        
        if st.button(f"🔁 重复歌曲 ({dup_count})", use_container_width=True, 
                     type="primary" if st.session_state.selected_function == "duplicates" else "secondary"):
            st.session_state.selected_function = "duplicates"
            st.session_state.dup_page = 0
            st.rerun()
        
        if st.button(f"🎧 仅 MP3 ({mp3_count})", use_container_width=True,
                     type="primary" if st.session_state.selected_function == "mp3only" else "secondary"):
            st.session_state.selected_function = "mp3only"
            st.session_state.mp3_page = 0
            st.rerun()
        
        st.divider()
        
        # 统计信息
        st.markdown("### 📊 库统计")
        st.metric("总文件数", len(st.session_state.df))
        st.metric("唯一歌曲", st.session_state.df["song_key"].nunique())
        st.metric("格式类型", st.session_state.df["format"].nunique())
    
if st.session_state.selected_function is None:
    st.subheader("🎯 清理建议", divider="blue")
    
    if st.session_state.df is not None:
        col1, col2, col3 = st.columns(3, gap="large")
        with col1:
            st.metric("📦 文件总数", len(st.session_state.df))
        with col2:
            st.metric("🎵 唯一歌曲", st.session_state.df["song_key"].nunique())
        with col3:
            mp3_df = find_mp3_only(st.session_state.df)
            mp3_count = mp3_df["song_key"].nunique() if len(mp3_df) > 0 else 0
            st.metric("🎧 仅 MP3 歌曲", mp3_count)
        
        st.divider()
    st.info("👈 请在左侧选择分析功能查看详细结果")
    st.stop()

df = st.session_state.df

# ========== 页面路由 ==========
if st.session_state.selected_function is None:
    show_dashboard(df, find_mp3_only)

elif st.session_state.selected_function == "duplicates":
    dup_df = find_duplicates(df)
    show_duplicates_view(dup_df, df, delete_files)

# ========== 仅 MP3 歌曲视图 ==========
elif st.session_state.selected_function == "mp3only":
    mp3_df = find_mp3_only(df)
    show_mp3_view(mp3_df, delete_files)
