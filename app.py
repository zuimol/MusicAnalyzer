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

elif st.session_state.selected_function == "mp3only":
    mp3_df = find_mp3_only(df)
    show_mp3_view(mp3_df, delete_files)
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
            
            col1, col2 = st.columns([4, 1], gap="small")
            with col1:
                st.markdown(f"### 🎵 {song_key}")
            with col2:
                copy_text = f"{title} - {artist}" if artist else title
                # 使用 HTML/JavaScript 实现真实复制
                st.markdown(f"""
                <button id="btn_{song_key}" onclick="
                    const text = '{copy_text}';
                    navigator.clipboard.writeText(text).then(() => {{
                        alert('✅ 已复制: ' + text);
                    }}).catch(err => {{
                        console.error('复制失败:', err);
                    }});
                " style="padding: 5px 10px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">
                📋 复制
                </button>
                """, unsafe_allow_html=True)
            
            st.dataframe(
                group[["file_name", "format", "bitrate", "sample_rate", "duration"]],
                use_container_width=True,
                height=300
            )
            st.divider()
        
        with st.form("form_duplicates"):
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
        
        # 获取当前页的数据
        start_idx = st.session_state.mp3_page * items_per_page
        end_idx = min(start_idx + items_per_page, len(mp3_df))
        page_df = mp3_df.iloc[start_idx:end_idx]
        
        # 显示表格和复制按钮（在 form 外面）
        st.markdown("**歌曲列表**")
        
        copy_col1, copy_col2 = st.columns([5, 1])
        with copy_col1:
            pass
        with copy_col2:
            st.caption("**复制**")
        
        for idx, (_, row) in enumerate(page_df.iterrows()):
            cols = st.columns([3, 1, 1, 1, 1])
            with cols[0]:
                st.caption(f"{row['title']} - {row['artist']}")
            with cols[1]:
                st.caption(f"{row['bitrate']}")
            with cols[2]:
                st.caption(f"{row['duration']:.0f}s")
            with cols[3]:
                st.caption(f"{row['file_name']}")
            with cols[4]:
                copy_text = f"{row['title']} - {row['artist']}"
                # 使用 HTML/JavaScript 实现真实复制
                st.markdown(f"""
                <button onclick="
                    const text = '{copy_text}';
                    navigator.clipboard.writeText(text).then(() => {{
                        alert('✅ 已复制: ' + text);
                    }}).catch(err => {{
                        console.error('复制失败:', err);
                    }});
                " style="padding: 5px 8px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px;">
                📋
                </button>
                """, unsafe_allow_html=True)
        
        st.divider()
        
        with st.form("form_mp3only"):
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
