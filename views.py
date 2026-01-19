"""
MusicAnalyzer 页面视图
处理重复歌曲和 MP3 页面的显示逻辑
"""

import streamlit as st
import pandas as pd
from analyzer import get_format_priority, get_duplicates_to_delete
from components import render_copy_button, render_copy_icon_button
from config import PAGINATION


def show_duplicates_view(dup_df: pd.DataFrame, df: pd.DataFrame, delete_files_fn):
    """
    显示重复歌曲视图
    
    Args:
        dup_df: 重复歌曲数据框
        df: 完整数据框
        delete_files_fn: 删除文件函数
    """
    st.warning(f"⚠️ 找到 {len(dup_df)} 个重复文件（{dup_df['song_key'].nunique()} 首歌曲有重复）")
    
    if len(dup_df) == 0:
        st.success("✅ 没有重复歌曲，库很干净！")
        return
    
    # 分页设置
    items_per_page = PAGINATION["duplicates_per_page"]
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

    # 获取当前页的数据
    start_idx = st.session_state.dup_page * items_per_page
    end_idx = min(start_idx + items_per_page, len(unique_songs))
    page_songs = unique_songs[start_idx:end_idx]
    
    # 按 song_key 分组显示（在 form 外面）
    for song_key in page_songs:
        group = dup_df[dup_df["song_key"] == song_key].copy()
        group["priority"] = group["format"].apply(get_format_priority)
        group = group.sort_values("priority", ascending=False)
        
        # 提取标题和艺术家
        title = group.iloc[0]["title"] if "title" in group.columns else song_key
        artist = group.iloc[0]["artist"] if "artist" in group.columns else ""
        st.markdown(f"####  {song_key}")
        
        # 先获取当前分组的数据行数，计算适配的高度
        row_count = len(group[["file_name", "format", "bitrate", "sample_rate", "duration"]])
        # 每行约35px高度，表头约38px，最小高度设为80px避免过矮
        table_height = max(row_count * 35 + 38, 80)

        # 渲染自适应高度的表格
        st.dataframe(
            group[["file_name", "format", "bitrate", "sample_rate", "duration"]],
            use_container_width=True,
            height=table_height  # 用计算出的高度替代固定值200
        )
    
    with st.form("form_duplicates"):
        if st.form_submit_button("🗑️ 删除", use_container_width=True, type="secondary"):
            files_to_delete = get_duplicates_to_delete(df)
            if len(files_to_delete) > 0:
                deleted, failed = delete_files_fn(files_to_delete)
                st.success(f"✅ 已删除 {len(deleted)} 个文件")
                if failed:
                    st.error(f"❌ 删除失败 {len(failed)} 个文件:")
                    for path, error in failed:
                        st.error(f"  {path}: {error}")
                st.info("请重新扫描以更新数据")


def show_mp3_view(mp3_df: pd.DataFrame, delete_files_fn):
    """
    显示仅 MP3 歌曲视图
    
    Args:
        mp3_df: MP3 歌曲数据框
        delete_files_fn: 删除文件函数
    """
    
    if len(mp3_df) == 0:
        st.success("✅ 没有仅 MP3 的歌曲，音质很不错！")
        return
    
    st.warning(f"⚠️ 找到 {mp3_df['song_key'].nunique()} 首歌曲仅有 MP3 版本（建议升级）")
    
    # 分页设置
    items_per_page = PAGINATION["mp3_per_page"]
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
    
    # 获取当前页的数据
    start_idx = st.session_state.mp3_page * items_per_page
    end_idx = min(start_idx + items_per_page, len(mp3_df))
    page_df = mp3_df.iloc[start_idx:end_idx]
    
    # 显示表格和复制按钮（在 form 外面）
    st.markdown("**歌曲列表**")
    
    copy_col1, copy_col2 = st.columns([4, 1])
    with copy_col1:
        pass
    with copy_col2:
        st.caption("**复制**")
    
    for idx, (_, row) in enumerate(page_df.iterrows()):
        cols = st.columns([3, 1, 1, 1])
        with cols[0]:
            st.caption(f"{row['title']} - {row['artist']}")
        with cols[1]:
            st.caption(f"{row['bitrate']}")
        with cols[2]:
            st.caption(f"{row['duration']:.0f}s")
        with cols[3]:
            st.caption(f"{row['file_name']}")
    
    st.divider()
    
    with st.form("form_mp3only"):
        if st.form_submit_button("🗑️ 删除", use_container_width=True, type="secondary"):
            deleted, failed = delete_files_fn(mp3_df)
            st.success(f"✅ 已删除 {len(deleted)} 个文件")
            if failed:
                st.error(f"❌ 删除失败 {len(failed)} 个文件:")
                for path, error in failed:
                    st.error(f"  {path}: {error}")
            st.info("请重新扫描以更新数据")


def show_dashboard(df: pd.DataFrame, find_mp3_only_fn):
    """
    显示主仪表板
    
    Args:
        df: 完整数据框
        find_mp3_only_fn: 查找 MP3 函数
    """
    if df is None:
        st.info("👈 请在左侧选择分析功能查看详细结果")
        st.stop()
    
    st.subheader("🎯 清理建议", divider="blue")
    
    col1, col2, col3 = st.columns(3, gap="large")
    with col1:
        st.metric("📦 文件总数", len(df))
    with col2:
        st.metric("🎵 唯一歌曲", df["song_key"].nunique())
    with col3:
        mp3_df = find_mp3_only_fn(df)
        mp3_count = mp3_df["song_key"].nunique() if len(mp3_df) > 0 else 0
        st.metric("🎧 仅 MP3 歌曲", mp3_count)
    
    st.divider()
    st.info("👈 请在左侧选择分析功能查看详细结果")
    st.stop()
