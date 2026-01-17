
import streamlit as st
import pandas as pd
import os

from scanner import scan_music
from analyzer import analyze, find_duplicates, find_multi_version, find_mp3_only

st.set_page_config(page_title="🎵 音乐库分析 Demo", layout="wide")
st.title("🎵 本地音乐库分析 Demo（支持删除文件）")

def list_dirs(path):
    try:
        return [
            os.path.join(path, d)
            for d in os.listdir(path)
            if os.path.isdir(os.path.join(path, d))
        ]
    except Exception:
        return []

# 目录选择
root_dir = st.text_input("请输入父目录（用于下拉提示）：", value="G:/")
dirs = list_dirs(root_dir)
music_dir = st.selectbox("请选择音乐根目录：", dirs)

# 会话状态
if "df" not in st.session_state:
    st.session_state.df = None

if st.button("开始扫描"):
    if not music_dir:
        st.warning("请先选择音乐目录")
        st.stop()

    with st.spinner("正在扫描音乐文件..."):
        data = scan_music(music_dir)
        df = pd.DataFrame(data)
        df = analyze(df)

    st.session_state.df = df
    st.success(f"扫描完成，共 {len(df)} 个音频文件")

df = st.session_state.df
if df is None:
    st.stop()

# 统计信息
col1, col2, col3, col4 = st.columns(4)
col1.metric("文件总数", len(df))
col2.metric("唯一歌曲数", df["song_key"].nunique())
col3.metric("多版本歌曲数", find_multi_version(df)["song_key"].nunique())
col4.metric("仅 MP3 歌曲数", find_mp3_only(df)["song_key"].nunique())

# 删除工具函数
def delete_files(rows):
    deleted = []
    for path in rows["path"]:
        try:
            os.remove(path)
            deleted.append(path)
        except Exception as e:
            st.error(f"删除失败: {path} ({e})")
    return deleted

# Tabs
tab1, tab2, tab3 = st.tabs([
    "🔁 重复歌曲（可删）",
    "🎚 多版本歌曲（可删）",
    "🎧 仅 MP3 歌曲（可删）"
])

with tab1:
    dup_df = find_duplicates(df)
    st.dataframe(dup_df, use_container_width=True)

    if st.button("删除选中的重复文件"):
        deleted = delete_files(dup_df)
        st.success(f"已删除 {len(deleted)} 个文件，请重新扫描")

with tab2:
    mv_df = find_multi_version(df)
    st.dataframe(mv_df, use_container_width=True)

    if st.button("删除多版本中的选中文件"):
        deleted = delete_files(mv_df)
        st.success(f"已删除 {len(deleted)} 个文件，请重新扫描")

with tab3:
    mp3_df = find_mp3_only(df)
    st.dataframe(mp3_df, use_container_width=True)

    if st.button("删除仅 MP3 歌曲文件"):
        deleted = delete_files(mp3_df)
        st.success(f"已删除 {len(deleted)} 个文件，请重新扫描")
