import pandas as pd


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


def find_multi_version(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("song_key")
        .filter(lambda x: x["format"].nunique() > 1)
        .dropna(subset=["song_key"])
    )


def find_mp3_only(df: pd.DataFrame) -> pd.DataFrame:
    def only_mp3(group):
        return set(group["format"]) == {"mp3"}

    return (
        df.groupby("song_key")
        .filter(only_mp3)
        .dropna(subset=["song_key"])
    )
