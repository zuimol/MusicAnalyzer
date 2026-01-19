import pandas as pd

# 格式优先级（高到低）
FORMAT_PRIORITY = {
    "flac": 5,
    "wav": 4,
    "alac": 4,
    "aiff": 3,
    "aac": 2,
    "mp3": 1,
}

def get_format_priority(fmt):
    """获取格式优先级，高优先级的文件应该被保留"""
    return FORMAT_PRIORITY.get(fmt.lower(), 0)


def mark_files_to_delete(df: pd.DataFrame) -> pd.DataFrame:
    """
    标记重复文件中应该删除的文件
    保留优先级最高的，删除其他
    """
    df = df.copy()
    df["should_delete"] = False
    
    dup_df = df[df.duplicated("song_key", keep=False) & df["song_key"].notna()]
    
    for song_key in dup_df["song_key"].unique():
        group = dup_df[dup_df["song_key"] == song_key].copy()
        
        # 按优先级排序（降序）
        group["priority"] = group["format"].apply(get_format_priority)
        group = group.sort_values("priority", ascending=False)
        
        # 第一个是优先级最高的，应该保留
        # 其他都标记为删除
        indices_to_delete = group.iloc[1:].index
        df.loc[indices_to_delete, "should_delete"] = True
    
    return df


def get_duplicates_to_delete(df: pd.DataFrame) -> pd.DataFrame:
    """
    返回标记为删除的重复文件
    （保留最高优先级的，删除其他）
    """
    return df[df.duplicated("song_key", keep=False) & df["should_delete"]]


def normalize_key(row):
    if not row["title"] or not row["artist"] or not row["duration"]:
        return None
    return f"{row['title'].lower()}|{row['artist'].lower()}|{round(row['duration'])}"


def analyze(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["song_key"] = df.apply(normalize_key, axis=1)
    return df


def find_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    return df[df.duplicated("song_key", keep=False) & df["song_key"].notna()]


def find_mp3_only(df: pd.DataFrame) -> pd.DataFrame:
    def only_mp3(group):
        return set(group["format"]) == {"mp3"}

    return (
        df.groupby("song_key")
        .filter(only_mp3)
        .dropna(subset=["song_key"])
    )
