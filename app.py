import streamlit as st
import pandas as pd

from scanner import scan_music
from analyzer import analyze, find_duplicates, find_multi_version, find_mp3_only


st.set_page_config(page_title="🎵 音乐库分析 Demo", layout="wide")

st.title("🎵 本地音乐库分析 Demo")

music_dir = st.text_input("请输入音乐根目录路径：", placeholder="例如：D:/Music")

if st.button("开始扫描"):
    if not music_dir:
        st.warning("请先输入音乐目录")
        st.stop()

    with st.spinner("正在扫描音乐文件..."):
        data = scan_music(music_dir)
        df = pd.DataFrame(data)
        df = analyze(df)

    st.success(f"扫描完成，共 {len(df)} 个音频文件")

    # 统计
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("文件总数", len(df))
    col2.metric("唯一歌曲数", df["song_key"].nunique())
    col3.metric("多版本歌曲数", find_multi_version(df)["song_key"].nunique())
    col4.metric("仅 MP3 歌曲数", find_mp3_only(df)["song_key"].nunique())

    tab1, tab2, tab3, tab4 = st.tabs([
        "📁 全部文件",
        "🔁 重复歌曲",
        "🎚 多版本歌曲",
        "🎧 仅 MP3 歌曲"
    ])

    with tab1:
        st.dataframe(df, use_container_width=True)

    with tab2:
        st.dataframe(find_duplicates(df), use_container_width=True)

    with tab3:
        st.dataframe(find_multi_version(df), use_container_width=True)

    with tab4:
        st.dataframe(find_mp3_only(df), use_container_width=True)
