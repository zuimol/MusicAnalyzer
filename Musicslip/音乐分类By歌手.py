import os
import shutil
from pathlib import Path
from mutagen import File

def get_artist_from_metadata(file_path):
    """
    从音乐文件的元数据中提取艺术家名称。

    参数：
        file_path (Path): 音乐文件的路径。

    返回：
        str: 艺术家名称，如果未找到则返回 "未知艺术家"。
    """
    try:
        audio = File(file_path)
        
        if audio is None:
            return "未知艺术家"
        
        # 尝试多种可能的艺术家字段名（支持MP3的ID3v2标签格式）
        artist_keys = ["artist", "TPE1", "TPE2", "©ART", "\xa9ART", "ARTIST"]
        
        for key in artist_keys:
            if key in audio:
                try:
                    artist_value = audio[key][0] if isinstance(audio[key], list) else str(audio[key])
                    return str(artist_value)
                except Exception:
                    continue
        
        return "未知艺术家"
            
    except Exception as e:
        print(f"无法读取文件 {file_path} 的元数据: {e}")
    return "未知艺术家"

def organize_music_files_by_artist(directory, include_subdirectories=True):
    """
    遍历指定目录下的音乐文件，根据艺术家生成对应的文件夹，并将音乐文件移动到相应文件夹中。

    参数：
        directory (str): 包含音乐文件的目录路径。
        include_subdirectories (bool): 是否包含子目录。
    """
    # 检查目录是否存在
    if not os.path.exists(directory):
        print(f"目录 '{directory}' 不存在。")
        return

    # 支持的音乐文件扩展名
    music_extensions = {".mp3", ".flac", ".wav", ".aac", ".m4a", ".ogg"}

    # 将会创建的文件夹集合
    folders_to_create = set()

    # 日志记录
    log_entries = []

    # 遍历目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = Path(root) / file

            # 检查文件是否为音乐文件
            if file_path.suffix.lower() in music_extensions:
                # 检查文件名是否包含 * 字符，如果包含则跳过
                if "*" in file:
                    skip_reason = f"文件名包含 '*' 字符"
                    print(f"跳过文件 '{file_path}'，原因：{skip_reason}")
                    log_entries.append(f"跳过文件 '{file_path}'，原因：{skip_reason}")
                    continue

                # 从文件元数据中提取艺术家名称
                artist = get_artist_from_metadata(file_path)

                # 打印读取到的艺术家名称
                print(f"读取文件 '{file_path}' 的艺术家: {artist}")

                # 如果艺术家名称是 "未知艺术家"，跳过处理
                if artist == "未知艺术家":
                    log_entries.append(f"跳过文件 '{file_path}'，原因：未找到艺术家信息")
                    continue

                # 如果艺术家名称包含多个艺术家（例如多人共同创作），选取第一个艺术家为准
                if ";" in artist or "," in artist:
                    artist = artist.split(";")[0] if ";" in artist else artist.split(",")[0]
                    log_entries.append(f"文件 '{file_path}' 的艺术家已修改为 '{artist}'（多人艺术家处理）")

                # 检查艺术家名称是否包含 * 字符，如果包含则跳过
                if "*" in artist:
                    skip_reason = f"艺术家名称包含 '*' 字符（艺术家：'{artist}'）"
                    print(f"跳过文件 '{file_path}'，原因：{skip_reason}")
                    log_entries.append(f"跳过文件 '{file_path}'，原因：{skip_reason}")
                    continue

                # 准备艺术家文件夹路径
                artist_folder = Path(directory) / artist
                folders_to_create.add(artist_folder)

                # 准备目标路径
                destination = artist_folder / file

                # 确保目标文件夹存在
                artist_folder.mkdir(parents=True, exist_ok=True)

                # 移动文件并记录日志
                shutil.move(str(file_path), str(destination))
                log_entries.append(f"文件 '{file_path}' 已移动到 '{destination}'")

        # 如果不包含子目录，则只遍历当前目录
        if not include_subdirectories:
            break

    # 输出将会创建的文件夹
    print("将会创建以下文件夹：")
    for folder in folders_to_create:
        print(folder)
        folder.mkdir(exist_ok=True)  # 创建文件夹

    # 输出操作日志
    log_file = Path(directory) / "操作日志.txt"
    with open(log_file, "w", encoding="utf-8") as log:
        log.write("本次操作详细日志：\n")
        log.write("\n".join(log_entries))

    print("音乐文件已按艺术家分类整理，详细日志已生成。")

# 示例用法
if __name__ == "__main__":
    organize_music_files_by_artist("G:\\Music\\11common", include_subdirectories=False)
