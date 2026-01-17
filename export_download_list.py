"""
音乐升级下载清单生成器
用于导出需要升级的歌曲列表，便于在酷我音乐中批量搜索下载
"""

import pandas as pd
import json
from pathlib import Path
from scanner import scan_music
from analyzer import analyze, find_duplicates, find_multi_version, find_mp3_only, get_format_priority
from datetime import datetime

class DownloadListGenerator:
    def __init__(self, music_path="G:\\music"):
        self.music_path = music_path
        self.df = None
        self.export_dir = Path("./exports")
        self.export_dir.mkdir(exist_ok=True)
        
    def scan_and_analyze(self):
        """扫描并分析音乐库"""
        print(f"🔍 正在扫描: {self.music_path}")
        music_list = scan_music(self.music_path)
        if not music_list:
            print("❌ 未找到音乐文件!")
            return False
        
        self.df = pd.DataFrame(music_list)
        self.df = analyze(self.df)
        print(f"✅ 扫描完成，找到 {len(self.df)} 个文件")
        return True
    
    def generate_mp3_upgrade_list(self):
        """生成仅MP3歌曲的升级清单"""
        print("\n📝 生成仅MP3歌曲升级清单...")
        mp3_df = find_mp3_only(self.df)
        
        if len(mp3_df) == 0:
            print("✅ 没有仅MP3的歌曲，无需升级")
            return None
        
        # 按艺术家分组
        result = []
        for song_key in sorted(mp3_df['song_key'].unique()):
            songs = mp3_df[mp3_df['song_key'] == song_key]
            first = songs.iloc[0]
            result.append({
                "song_key": song_key,
                "title": first.get("title", ""),
                "artist": first.get("artist", ""),
                "duration": first.get("duration", ""),
                "current_bitrate": first.get("bitrate", ""),
                "file_name": first.get("file_name", ""),
                "priority": "🔴 高优先级"
            })
        
        result_df = pd.DataFrame(result)
        return result_df
    
    def generate_multi_version_list(self):
        """生成多版本歌曲清单（可能的最优化选择）"""
        print("\n📝 生成多版本歌曲清单...")
        mv_df = find_multi_version(self.df)
        
        if len(mv_df) == 0:
            print("✅ 所有歌曲格式统一")
            return None
        
        # 按歌曲统计信息
        result = []
        for song_key in sorted(mv_df['song_key'].unique()):
            songs = mv_df[mv_df['song_key'] == song_key].copy()
            songs["priority"] = songs["format"].apply(get_format_priority)
            songs = songs.sort_values("priority", ascending=False)
            
            best = songs.iloc[0]
            current = best.get("format", "")
            
            result.append({
                "song_key": song_key,
                "title": best.get("title", ""),
                "artist": best.get("artist", ""),
                "formats": ", ".join(sorted(songs["format"].unique())),
                "best_format": current,
                "version_count": len(songs),
                "priority": "🟡 中优先级"
            })
        
        result_df = pd.DataFrame(result)
        return result_df
    
    def export_to_csv(self, data_dict):
        """导出为CSV文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for name, df in data_dict.items():
            if df is not None:
                filepath = self.export_dir / f"{name}_{timestamp}.csv"
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
                print(f"✅ 导出 CSV: {filepath}")
                print(f"   📊 共 {len(df)} 条记录\n")
    
    def export_to_json(self, data_dict):
        """导出为JSON文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        all_data = {}
        for name, df in data_dict.items():
            if df is not None:
                all_data[name] = df.to_dict('records')
        
        filepath = self.export_dir / f"download_list_{timestamp}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        print(f"✅ 导出 JSON: {filepath}\n")
    
    def export_to_txt(self, data_dict):
        """导出为易读的TXT文件（便于复制到模拟器）"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.export_dir / f"download_list_{timestamp}.txt"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("🎵 音乐升级下载清单\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")
            
            for name, df in data_dict.items():
                if df is not None:
                    f.write(f"\n{name.upper()}\n")
                    f.write("-"*60 + "\n")
                    
                    for idx, row in df.iterrows():
                        f.write(f"\n【{idx+1}】 {row.get('song_key', row.get('title', ''))}\n")
                        for col in df.columns:
                            if col != 'song_key':
                                val = row[col]
                                if pd.notna(val):
                                    f.write(f"  {col}: {val}\n")
                    
                    f.write(f"\n小计: {len(df)} 首歌曲\n")
                    f.write("="*60 + "\n")
        
        print(f"✅ 导出 TXT: {filepath}")
        print(f"   📝 格式化清单，便于手动操作\n")
    
    def print_summary(self, data_dict):
        """打印总结信息"""
        print("\n📊 升级清单汇总:")
        print("-"*60)
        
        total = 0
        for name, df in data_dict.items():
            if df is not None:
                count = len(df)
                total += count
                print(f"  {name}: {count} 首歌曲")
        
        print("-"*60)
        print(f"  总计: {total} 首歌曲需要升级\n")
    
    def run(self, export_formats=['csv', 'txt', 'json']):
        """运行完整流程"""
        print("🎵 音乐库升级清单生成器\n")
        
        if not self.scan_and_analyze():
            return
        
        # 生成清单
        data = {
            "仅MP3歌曲": self.generate_mp3_upgrade_list(),
            "多版本歌曲": self.generate_multi_version_list()
        }
        
        # 打印统计
        self.print_summary(data)
        
        # 导出
        if 'csv' in export_formats:
            self.export_to_csv(data)
        if 'txt' in export_formats:
            self.export_to_txt(data)
        if 'json' in export_formats:
            self.export_to_json(data)
        
        print("✅ 所有清单已生成，保存在 ./exports 目录\n")
        print("💡 使用建议:")
        print("  1. 打开 TXT 文件查看清单")
        print("  2. 复制歌曲名称到酷我音乐搜索")
        print("  3. 下载最高质量版本（FLAC 优先）")
        print("  4. 将下载的文件放到原歌曲目录")
        print("  5. 再次运行 MusicAnalyzer 验证升级效果\n")

if __name__ == "__main__":
    # 修改路径为你的音乐目录
    generator = DownloadListGenerator(music_path="G:\\music")
    generator.run(export_formats=['csv', 'txt', 'json'])
