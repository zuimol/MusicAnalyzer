# 🎵 音乐升级下载工具使用指南

## 功能说明

### 1. **export_download_list.py** - 下载清单生成器
自动生成需要升级的歌曲清单，支持多种导出格式。

#### 使用方式

**方式一：直接运行**
```bash
python export_download_list.py
```

**方式二：在代码中调用**
```python
from export_download_list import DownloadListGenerator

# 创建生成器
generator = DownloadListGenerator(music_path="G:\\music")

# 运行生成流程
generator.run(export_formats=['csv', 'txt', 'json'])
```

#### 输出文件说明

脚本会在 `./exports/` 目录下生成：

| 文件格式 | 用途 | 说明 |
|---------|------|------|
| `*.csv` | 数据分析 | 可在 Excel 中打开，便于统计和排序 |
| `*.txt` | 手动查看 | 格式化清单，便于复制粘贴到酷我音乐 |
| `*.json` | 程序处理 | 便于后续脚本自动化处理 |

#### 清单内容

**仅MP3歌曲清单** 🔴 高优先级
- 列出所有仅有MP3格式的歌曲
- 这些歌曲质量最低，最需要升级
- 建议下载 FLAC 或 WAV 版本

**多版本歌曲清单** 🟡 中优先级
- 列出拥有多个格式版本的歌曲
- 显示当前拥有的所有格式
- 标记最优格式（优先级最高的版本）

---

## 🚀 工作流程

### 第1步：生成清单
```bash
python export_download_list.py
```
↓

### 第2步：在酷我音乐中搜索和下载
1. 打开 `exports/download_list_*.txt` 文件
2. 复制歌曲名称和艺术家
3. 在酷我音乐中搜索
4. 选择 **FLAC 或 WAV** 版本下载（优先 FLAC）
5. 保存到电脑（不是模拟器内存）

### 第3步：整理下载的文件
1. 将下载的新文件移到原歌曲所在目录
2. 或替换原文件（如果需要清理空间）

### 第4步：验证升级
```bash
# 启动 Streamlit 应用
streamlit run app.py
```
- 再次扫描音乐库
- 检查"多版本歌曲"和"仅MP3歌曲"数量是否减少

---

## 📊 清单示例

### TXT 格式（易读）
```
🎵 音乐升级下载清单
生成时间: 2026-01-17 10:30:45
============================================================

仅MP3歌曲
------------------------------------------------------------

【1】 Believer|Imagine Dragons|209
  title: Believer
  artist: Imagine Dragons
  duration: 209
  current_bitrate: 320kbps
  file_name: Believer.mp3
  priority: 🔴 高优先级

【2】 Blinding Lights|The Weeknd|200
  ...

小计: 45 首歌曲
============================================================
```

### CSV 格式（数据分析）
```
song_key,title,artist,duration,current_bitrate,file_name,priority
"Believer|Imagine Dragons|209","Believer","Imagine Dragons",209,"320kbps","Believer.mp3","🔴 高优先级"
...
```

---

## 💡 下载建议

### 优先级顺序
1. 🔴 **仅MP3歌曲** - 必须升级
2. 🟡 **多版本歌曲** - 补全高质量版本
3. 其他 - 保持现状

### 格式优先级
1. **FLAC** (无损，最佳) 
2. **WAV** (无损，较大)
3. **ALAC** (无损，Mac友好)
4. **AAC** (有损，中等质量)
5. **MP3** (有损，最低质量)

### 下载提示
- ✅ 从酷我音乐下载 FLAC 版本时通常需要付费会员
- ✅ 某些歌曲可能没有 FLAC 版本，选最高可用质量
- ✅ 下载前检查比特率（320kbps MP3 优于 128kbps）
- ❌ 避免重复下载同一首歌

---

## 🔧 进阶用法

### 自定义导出

```python
from export_download_list import DownloadListGenerator

generator = DownloadListGenerator(music_path="D:\\MyMusic")

# 仅生成并分析
generator.scan_and_analyze()

# 获取需要升级的歌曲
mp3_list = generator.generate_mp3_upgrade_list()
mv_list = generator.generate_multi_version_list()

# 自定义处理
print(mp3_list.to_string())

# 仅导出 CSV
generator.export_to_csv({
    "upgrade_list": mp3_list
})
```

### 与 MusicAnalyzer 集成

下次将考虑在 app.py 中添加 "导出清单" 按钮，点击即可自动生成下载清单，无需手动运行脚本。

---

## 📝 注意事项

1. **文件位置**: 
   - 脚本会在 `./exports/` 目录下创建清单
   - 确保该目录有写入权限

2. **时间戳**: 
   - 每次运行会生成新文件（带时间戳）
   - 旧文件不会被覆盖

3. **编码**: 
   - 所有导出文件使用 UTF-8 编码
   - 支持中文、日文等多种字符

4. **性能**:
   - 首次扫描可能需要 1-5 分钟
   - 取决于音乐库文件数量

---

## ❓ 常见问题

**Q: 为什么有些歌曲没有出现在清单中？**  
A: 清单只包括需要升级的歌曲（仅MP3或多版本）。已经是最优格式的歌曲不会出现。

**Q: 可以一次下载所有歌曲吗？**  
A: 酷我音乐目前不支持批量下载。建议：
- 按艺术家分类
- 按优先级逐次下载
- 考虑付费加速下载速度

**Q: 下载后文件在哪里？**  
A: 
- 取决于酷我音乐的设置
- 通常在 `下载` 或 `我的音乐` 文件夹
- 检查浏览器下载目录

---

## 🎯 下一步

升级完成后，你可以：
1. ✅ 再次运行 MusicAnalyzer 验证
2. ✅ 清理旧的低质量文件
3. ✅ 更新音乐库元数据
4. ✅ 享受高质量音乐！

