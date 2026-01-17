
import streamlit as st
import pandas as pd
import os
from pathlib import Path

from scanner import scan_music
from analyzer import (
    analyze, find_duplicates, find_multi_version, find_mp3_only,
    mark_files_to_delete, get_duplicates_to_delete, get_format_priority
)

st.set_page_config(page_title="🎵 音乐库分析", layout="wide", initial_sidebar_state="expanded")

# ========== 页面样式 ==========
st.markdown("""
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
    .result-container {
        min-height: 70vh;
        overflow-y: auto;
    }
    
    /* 减少 divider 间距 */
    hr {
        margin: 0.5rem 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# ========== 初始化会话状态 ==========
if "current_path" not in st.session_state:
    st.session_state.current_path = "G:\\music"
if "df" not in st.session_state:
    st.session_state.df = None
if "dup_page" not in st.session_state:
    st.session_state.dup_page = 0
if "mv_page" not in st.session_state:
    st.session_state.mv_page = 0
if "mp3_page" not in st.session_state:
    st.session_state.mp3_page = 0
if "selected_function" not in st.session_state:
    st.session_state.selected_function = None

# ========== 工具函数 ==========
def delete_files(rows):
    """删除文件列表中的文件"""
    deleted = []
    failed = []
    for file_path in rows["file_path"]:
        try:
            os.remove(file_path)
            deleted.append(file_path)
        except Exception as e:
            failed.append((file_path, str(e)))
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
        mv_count = find_multi_version(st.session_state.df)["song_key"].nunique() if len(find_multi_version(st.session_state.df)) > 0 else 0
        mp3_count = find_mp3_only(st.session_state.df)["song_key"].nunique() if len(find_mp3_only(st.session_state.df)) > 0 else 0
        
        st.markdown("### 🎯 分析功能")
        
        if st.button(f"🔁 重复歌曲 ({dup_count})", use_container_width=True, 
                     type="primary" if st.session_state.selected_function == "duplicates" else "secondary"):
            st.session_state.selected_function = "duplicates"
            st.session_state.dup_page = 0
            st.rerun()
        
        if st.button(f"🎚️ 多版本 ({mv_count})", use_container_width=True,
                     type="primary" if st.session_state.selected_function == "multiversion" else "secondary"):
            st.session_state.selected_function = "multiversion"
            st.session_state.mv_page = 0
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

# ========== 主区域内容 ==========
if st.session_state.df is None:
    st.info("💡 请在左侧选择目录并点击 '开始扫描'")
    st.stop()

# 如果没有选择功能，显示统计
if st.session_state.selected_function is None:
    st.subheader("🎯 清理建议", divider="blue")
    
    col1, col2, col3, col4 = st.columns(4, gap="large")
    with col1:
        st.metric("📦 文件总数", len(st.session_state.df))
    with col2:
        st.metric("🎵 唯一歌曲", st.session_state.df["song_key"].nunique())
    with col3:
        st.metric("🎚️ 多版本歌曲", find_multi_version(st.session_state.df)["song_key"].nunique())
    with col4:
        st.metric("🎧 仅 MP3 歌曲", find_mp3_only(st.session_state.df)["song_key"].nunique())
    
    st.divider()
    st.info("👈 请在左侧选择分析功能查看详细结果")
    st.stop()

df = st.session_state.df

# ========== 重复歌曲视图 ==========
if st.session_state.selected_function == "duplicates":
    dup_df = find_duplicates(df)
    st.subheader("🔁 重复歌曲", divider="red")
    
    if len(dup_df) > 0:
        st.warning(f"⚠️ 找到 {len(dup_df)} 个重复文件（{dup_df['song_key'].nunique()} 首歌曲有重复）")
        
        # 分页设置
        items_per_page = 5
        unique_songs = sorted(dup_df["song_key"].unique())
        total_pages = (len(unique_songs) + items_per_page - 1) // items_per_page
        st.session_state.dup_page = min(st.session_state.dup_page, total_pages - 1)
        
        # 分页导航
        pagination_col = st.columns([1, 1.5, 1], gap="small")
        with pagination_col[0]:
            if st.button("⬅️", use_container_width=True, key="dup_prev"):
                st.session_state.dup_page = max(0, st.session_state.dup_page - 1)
                st.rerun()
        with pagination_col[1]:
            st.markdown(f"<div style='text-align:center; padding: 8px;'><b>第 {st.session_state.dup_page + 1}/{total_pages} 页</b></div>", unsafe_allow_html=True)
        with pagination_col[2]:
            if st.button("➡️", use_container_width=True, key="dup_next"):
                st.session_state.dup_page = min(total_pages - 1, st.session_state.dup_page + 1)
                st.rerun()
        
        st.divider()
        
        with st.form("form_duplicates"):
            # 获取当前页的数据
            start_idx = st.session_state.dup_page * items_per_page
            end_idx = min(start_idx + items_per_page, len(unique_songs))
            page_songs = unique_songs[start_idx:end_idx]
            
            # 按 song_key 分组显示
            for song_key in page_songs:
                group = dup_df[dup_df["song_key"] == song_key].copy()
                group["priority"] = group["format"].apply(get_format_priority)
                group = group.sort_values("priority", ascending=False)
                
                st.markdown(f"### 🎵 {song_key}")
                st.dataframe(
                    group[["file_name", "format", "bitrate", "sample_rate", "duration"]],
                    use_container_width=True,
                    height=300
                )
                st.divider()
            
            if st.form_submit_button("🗑️ 删除", use_container_width=True, type="secondary"):
                files_to_delete = get_duplicates_to_delete(df)
                if len(files_to_delete) > 0:
                    deleted, failed = delete_files(files_to_delete)
                    st.success(f"✅ 已删除 {len(deleted)} 个文件")
                    if failed:
                        st.error(f"❌ 删除失败 {len(failed)} 个文件:")
                        for path, error in failed:
                            st.error(f"  {path}: {error}")
                    st.info("请重新扫描以更新数据")
    else:
        st.success("✅ 没有重复歌曲，库很干净！")

# ========== 多版本歌曲视图 ==========
elif st.session_state.selected_function == "multiversion":
    mv_df = find_multi_version(df)
    st.subheader("🎚️ 多版本歌曲", divider="orange")
    
    if len(mv_df) > 0:
        st.warning(f"⚠️ 找到 {mv_df['song_key'].nunique()} 首歌曲有多个版本")
        
        # 分页设置
        items_per_page = 5
        unique_songs = sorted(mv_df["song_key"].unique())
        total_pages = (len(unique_songs) + items_per_page - 1) // items_per_page
        st.session_state.mv_page = min(st.session_state.mv_page, total_pages - 1)
        
        # 分页导航
        pagination_col = st.columns([1, 1.5, 1], gap="small")
        with pagination_col[0]:
            if st.button("⬅️", use_container_width=True, key="mv_prev"):
                st.session_state.mv_page = max(0, st.session_state.mv_page - 1)
                st.rerun()
        with pagination_col[1]:
            st.markdown(f"<div style='text-align:center; padding: 8px;'><b>第 {st.session_state.mv_page + 1}/{total_pages} 页</b></div>", unsafe_allow_html=True)
        with pagination_col[2]:
            if st.button("➡️", use_container_width=True, key="mv_next"):
                st.session_state.mv_page = min(total_pages - 1, st.session_state.mv_page + 1)
                st.rerun()
        
        st.divider()
        
        with st.form("form_multiversion"):
            # 获取当前页的数据
            start_idx = st.session_state.mv_page * items_per_page
            end_idx = min(start_idx + items_per_page, len(unique_songs))
            page_songs = unique_songs[start_idx:end_idx]
            
            # 按 song_key 分组显示
            for song_key in page_songs:
                song_data = mv_df[mv_df["song_key"] == song_key]
                st.markdown(f"### 📀 {song_key}")
                st.dataframe(
                    song_data[["file_name", "format", "bitrate", "sample_rate", "duration"]],
                    use_container_width=True,
                    height=300
                )
                st.divider()
            
            if st.form_submit_button("🗑️ 删除", use_container_width=True, type="secondary"):
                deleted, failed = delete_files(mv_df)
                st.success(f"✅ 已删除 {len(deleted)} 个文件")
                if failed:
                    st.error(f"❌ 删除失败 {len(failed)} 个文件:")
                    for path, error in failed:
                        st.error(f"  {path}: {error}")
                st.info("请重新扫描以更新数据")
    else:
        st.success("✅ 所有歌曲格式统一！")

# ========== 仅 MP3 歌曲视图 ==========
elif st.session_state.selected_function == "mp3only":
    mp3_df = find_mp3_only(df)
    st.subheader("🎧 仅 MP3 歌曲", divider="blue")
    
    if len(mp3_df) > 0:
        st.warning(f"⚠️ 找到 {mp3_df['song_key'].nunique()} 首歌曲仅有 MP3 版本（建议升级）")
        
        # 分页设置
        items_per_page = 20
        total_pages = (len(mp3_df) + items_per_page - 1) // items_per_page
        st.session_state.mp3_page = min(st.session_state.mp3_page, total_pages - 1)
        
        # 分页导航
        pagination_col = st.columns([1, 1.5, 1], gap="small")
        with pagination_col[0]:
            if st.button("⬅️", use_container_width=True, key="mp3_prev"):
                st.session_state.mp3_page = max(0, st.session_state.mp3_page - 1)
                st.rerun()
        with pagination_col[1]:
            st.markdown(f"<div style='text-align:center; padding: 8px;'><b>第 {st.session_state.mp3_page + 1}/{total_pages} 页</b></div>", unsafe_allow_html=True)
        with pagination_col[2]:
            if st.button("➡️", use_container_width=True, key="mp3_next"):
                st.session_state.mp3_page = min(total_pages - 1, st.session_state.mp3_page + 1)
                st.rerun()
        
        st.divider()
        
        with st.form("form_mp3only"):
            # 获取当前页的数据
            start_idx = st.session_state.mp3_page * items_per_page
            end_idx = min(start_idx + items_per_page, len(mp3_df))
            page_df = mp3_df.iloc[start_idx:end_idx]
            
            st.dataframe(
                page_df[["file_name", "artist", "title", "bitrate", "duration"]],
                use_container_width=True,
                height=500
            )
            
            if st.form_submit_button("🗑️ 删除", use_container_width=True, type="secondary"):
                deleted, failed = delete_files(mp3_df)
                st.success(f"✅ 已删除 {len(deleted)} 个文件")
                if failed:
                    st.error(f"❌ 删除失败 {len(failed)} 个文件:")
                    for path, error in failed:
                        st.error(f"  {path}: {error}")
                st.info("请重新扫描以更新数据")
    else:
        st.success("✅ 没有仅 MP3 的歌曲，音质很不错！")
