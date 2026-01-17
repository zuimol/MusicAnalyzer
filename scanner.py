from pathlib import Path
from mutagen import File
import hashlib


SUPPORTED_EXT = {".mp3", ".flac", ".wav", ".m4a", ".ogg"}


def scan_music(root_dir: str) -> list[dict]:
    results = []

    for path in Path(root_dir).rglob("*"):
        if path.suffix.lower() not in SUPPORTED_EXT:
            continue

        try:
            audio = File(path, easy=True)
            info = File(path)

            duration = round(info.info.length, 2) if info and info.info else None
            bitrate = getattr(info.info, "bitrate", None)
            sample_rate = getattr(info.info, "sample_rate", None)

            results.append({
                "file_path": str(path),
                "file_name": path.name,
                "format": path.suffix.lower().replace(".", ""),
                "title": (audio.get("title", [None])[0] if audio else None),
                "artist": (audio.get("artist", [None])[0] if audio else None),
                "album": (audio.get("album", [None])[0] if audio else None),
                "duration": duration,
                "bitrate": bitrate,
                "sample_rate": sample_rate,
            })

        except Exception as e:
            print(f"读取失败: {path} -> {e}")

    return results
