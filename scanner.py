from pathlib import Path
from mutagen import File
import hashlib
import re


SUPPORTED_EXT = {".mp3", ".flac", ".wav", ".m4a", ".ogg"}


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除 Windows 不允许的字符
    
    Windows 不允许的字符: < > : " / \ | ? *
    
    Args:
        filename: 原始文件名或目录名
        
    Returns:
        清理后的文件名，可安全用于 Windows 文件系统
    """
    # Windows 不允许的字符
    invalid_chars = r'[<>:"/\\|?*]'
    # 替换为下划线或移除（这里替换为下划线以保持可读性）
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # 移除首尾空格和点（Windows 不允许）
    sanitized = sanitized.strip(' .')
    
    # 确保不为空（如果全部被移除，使用默认名称）
    if not sanitized:
        sanitized = "unknown"
    
    # Windows 保留名称（如 CON, PRN, AUX, NUL 等）
    reserved_names = {'CON', 'PRN', 'AUX', 'NUL',
                     'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
                     'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'}
    
    # 检查是否为保留名称（不区分大小写）
    if sanitized.upper() in reserved_names:
        sanitized = f"_{sanitized}_"
    
    # 限制长度（Windows 路径最大长度为 260 字符，但这里只限制文件名本身）
    # 通常文件名不超过 255 字符即可
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    
    return sanitized


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
