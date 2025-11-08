# Ebook Converter - 快速开始指南

这是 [ebook-converter](https://github.com/gryf/ebook-converter) 的增强版本，增加了友好的 Web 图形界面。

## 新增功能 ✨

### Web 图形界面
- 🖱️ **可视化操作** - 拖拽文件即可转换，无需记忆命令
- 📁 **单文件转换** - 简单直观的文件上传和格式选择
- 📚 **批量转换** - 一次性转换多个文件
- 🎨 **现代化设计** - 美观的渐变色界面
- 📥 **自动下载** - 转换完成后自动下载结果

### 保留原有功能
- ⌨️ **命令行支持** - 适合批量处理和自动化脚本
- 🔄 **多格式支持** - 支持 EPUB, MOBI, PDF, DOCX 等主流格式

## 快速开始

### 1. 安装

```bash
# 克隆或进入项目目录
cd /Users/hongyuwang/code/ebook-converter

# 确保虚拟环境已激活
source venv/bin/activate

# 如果还没有安装，运行：
# python3 -m venv venv
# source venv/bin/activate
# pip install .

# 重要：修复 lxml 库冲突问题
pip uninstall -y lxml
pip install --no-binary lxml lxml
```

### 2. 使用 Web 界面（推荐）

```bash
# 方式 1: 使用启动脚本（最简单）
./start_web.sh

# 方式 2: 使用命令
ebook-converter-web

# 方式 3: 使用 Python 模块
python -m ebook_converter.web_app
```

然后在浏览器中打开: **http://127.0.0.1:5001**

### 3. 使用命令行

```bash
# 单个文件转换
ebook-converter input.epub output.mobi

# 查看帮助
ebook-converter --help

# 批量转换示例（bash）
for file in *.epub; do
    ebook-converter "$file" "${file%.epub}.mobi"
done
```

## Web 界面截图

### 单文件转换
- 点击或拖拽文件到上传区域
- 选择输出格式（EPUB, MOBI, DOCX 等）
- 点击"开始转换"
- 自动下载转换后的文件

### 批量转换
- 选择多个文件
- 统一选择输出格式
- 查看每个文件的转换结果

## 支持的格式

| 输入格式 | 输出格式 |
|---------|---------|
| EPUB, MOBI, AZW3 | EPUB, MOBI |
| PDF | DOCX, TXT |
| DOCX, ODT | EPUB, MOBI, HTMLZ |
| HTML, TXT | 各种格式 |
| FB2, RTF, PDB, LRF | 各种格式 |

## 系统要求

- Python 3.10 或更高版本
- Liberation Fonts（macOS: `brew install --cask font-liberation`）
- Poppler 工具（macOS: `brew install poppler`）
- 100MB 磁盘空间（用于临时文件）

## 配置文件位置

- Web 应用: `ebook_converter/web_app.py`
- HTML 模板: `ebook_converter/templates/`
- 命令行工具: `ebook_converter/main.py`

## 常见问题

### 端口冲突
如果 5001 端口被占用，编辑 `ebook_converter/web_app.py`，修改 `port=5001` 为其他端口。

### 转换失败
- 检查文件格式是否正确
- 尝试使用命令行模式查看详细错误信息
- 确保文件大小不超过 100MB

### 批量转换慢
这是正常的，每个文件都需要单独处理。命令行模式可能更快。

## 技术细节

- **Web 框架**: Flask 3.1+
- **转换引擎**: 基于 Calibre 的转换核心
- **前端**: 原生 HTML5/CSS3/JavaScript
- **部署**: 开发服务器（个人使用）

## 进一步阅读

- [详细的 Web 界面文档](WEB_INTERFACE.md)
- [原项目 README](README.rst)
- [Calibre 转换文档](https://manual.calibre-ebook.com/conversion.html)

## 许可证

GPL-3.0-or-later（与原项目相同）

## 鸣谢

基于 [Calibre](https://calibre-ebook.com/) 项目的转换核心构建。
