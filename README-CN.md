# 电子书转换器 (Ebook Converter)

[![License](https://img.shields.io/badge/license-GPL3-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org)

一个功能强大的电子书格式转换工具，提供命令行和 Web 界面两种使用方式。本项目基于 [Calibre](https://calibre-ebook.com/) 的核心转换功能，专注于提供简洁、高效的电子书转换体验。

## ✨ 核心特性

- 🌐 **现代化 Web 界面** - 提供拖拽上传、实时预览的友好用户界面
- 📄 **PDF 输出增强** - 完整支持中文字体（楷体），保留 CSS 样式和排版
- 🎨 **高级格式化** - 自动保留文字颜色、对齐方式、缩进、字体样式等
- 🇨🇳 **完美中文支持** - 正确处理中文文件名和内容，无乱码
- 🚀 **后台服务模式** - 一键启动/停止 Web 服务，支持后台运行
- 📦 **批量转换** - 支持同时转换多个文件，提高工作效率
- 🔧 **命令行工具** - 保留传统 CLI 接口，适合自动化脚本

## 📋 支持格式

### 输入格式

| 格式 | 说明 | 扩展名 |
|------|------|--------|
| Microsoft Word | 2007 及以上版本 | `.docx` |
| EPUB | v2 和 v3 | `.epub` |
| LibreOffice | OpenDocument | `.odt` |
| 纯文本 | UTF-8 编码 | `.txt` |
| Mobipocket | Kindle 格式 | `.mobi` |
| Kindle | Amazon 专有格式 | `.azw3`, `.azw4` |
| FictionBook | 俄罗斯流行格式 | `.fb2` |
| HTML | 网页格式 | `.html`, `.htm` |
| PDF | Adobe PDF | `.pdf` |
| PalmOS | 多种 PalmOS 阅读器 | `.pdb` |
| RTF | 富文本格式 | `.rtf` |
| BBeB | 宽带电子书 | `.lrf` |

### 输出格式

| 格式 | 说明 | 特色功能 |
|------|------|----------|
| **PDF** | Adobe PDF | ⭐ 中文楷体字体、CSS 样式保留、封面图片、章节分页 |
| EPUB | v2 标准 | 兼容性最佳 |
| DOCX | Microsoft Word | 可编辑 |
| TXT | 纯文本 | 最小体积 |

## 🔧 系统要求

### 必需组件

- **Python 3.10** 或更高版本
- **Liberation Fonts** - 用于 PDF 渲染
- **Poppler 工具** - `pdftohtml`, `pdfinfo`, `pdftoppm`（用于 PDF 输入）
- **系统库**:
  - `libxml2-dev` - XML 处理
  - `libxslt-dev` - XSLT 转换

### Python 依赖包

核心依赖（自动安装）：

```txt
beautifulsoup4     # HTML/XML 解析
css-parser         # CSS 样式解析
filelock           # 文件锁定
flask>=3.0         # Web 框架
html2text          # HTML 转文本
html5-parser       # HTML5 解析
msgpack            # 序列化
odfpy              # ODF 格式支持
pillow             # 图像处理
python-dateutil    # 日期处理
reportlab>=4.0     # PDF 生成（中文支持）
setuptools         # 打包工具
tinycss            # CSS 解析
```

## 📦 安装

### 方式一：标准安装（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/why198546/ebook-converter.git
cd ebook-converter

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 3. 安装项目及所有依赖
pip install .

# 4. 验证安装
ebook-converter --help
```

### 方式二：开发模式

```bash
# 可编辑模式安装，方便开发调试
pip install -e .
```

## 🚀 快速开始

### Web 界面模式（推荐新手）

1. **启动服务**

   ```bash
   source venv/bin/activate  # 激活虚拟环境
   ebook-convert             # 启动 Web 服务
   ```

2. **访问界面**

   浏览器会自动打开 `http://127.0.0.1:5001`

3. **转换文件**

   - 单文件转换：拖拽文件到上传区域
   - 批量转换：点击"批量转换"选择多个文件

4. **停止服务**

   ```bash
   ebook-stop    # 停止服务
   ebook-status  # 查看服务状态
   ```

### 命令行模式（适合自动化）

```bash
# 基本用法
ebook-converter input.epub output.pdf

# 指定格式转换
ebook-converter book.mobi book.pdf
ebook-converter book.docx book.epub

# 批量转换（Shell 脚本）
for file in *.mobi; do
    ebook-converter "$file" "${file%.mobi}.pdf"
done
```

## 🎨 PDF 转换高级功能

当转换为 PDF 格式时，本工具提供以下增强功能：

### 1. 中文字体支持

- **内置楷体字体** - 完美显示简体和繁体中文
- **无需额外配置** - 开箱即用
- **高质量渲染** - 清晰的字体显示

### 2. CSS 样式保留

自动识别并保留以下 CSS 属性：

| CSS 属性 | 支持的值 | 示例 |
|---------|---------|------|
| `color` | 颜色名称、十六进制 | `orange`, `#FF5733` |
| `text-align` | left, center, right, justify | 文本对齐方式 |
| `text-indent` | em, pt, px | `2em`, `20pt` |
| `margin` | em, pt, px | 段落间距 |
| `font-size` | em, pt, px, 命名大小 | `1.2em`, `14pt`, `large` |
| `font-family` | 字体名称 | `楷体`, `SimKai` |
| `font-weight` | bold, normal | 粗体 |
| `font-style` | italic, normal | 斜体 |

### 3. 内容结构

- **封面图片** - 自动提取并调整尺寸（17cm × 23.9cm）
- **章节分页** - 每章开始新的一页
- **目录保留** - 维护原书的章节结构
- **图片嵌入** - 自动处理和优化图片

### 4. 文件名处理

- **Unicode 支持** - 完美处理中文文件名
- **特殊字符** - 自动处理括号、空格等特殊字符
- **下载保留** - 下载时保持原始文件名

### 示例效果

```python
# 转换前（MOBI/EPUB）
<p style="color:orange; text-indent:2em; text-align:center">
    这是一段橙色的居中文本，首行缩进2字符
</p>

# 转换后（PDF）
✓ 保留橙色
✓ 保留居中对齐
✓ 保留首行缩进
✓ 使用楷体字体显示中文
```

## 📖 使用示例

### 示例 1：转换中文 MOBI 到 PDF

```bash
ebook-converter "奇妙的3D世界.mobi" "奇妙的3D世界.pdf"
```

**结果**：
- ✅ 中文字符完美显示（楷体）
- ✅ 保留原书的颜色和排版
- ✅ 包含封面图片
- ✅ 21 个章节自动分页
- ✅ 文件名保持中文

### 示例 2：批量转换 EPUB 到 PDF

```bash
# 使用 Web 界面
1. 访问 http://127.0.0.1:5001
2. 点击"批量转换"
3. 选择多个 EPUB 文件
4. 选择输出格式为 PDF
5. 点击"开始转换"

# 或使用命令行
for file in *.epub; do
    ebook-converter "$file" "${file%.epub}.pdf"
done
```

### 示例 3：自动化脚本

```bash
#!/bin/bash
# convert-all.sh - 转换指定目录下的所有电子书为 PDF

INPUT_DIR="./ebooks"
OUTPUT_DIR="./pdf_output"

mkdir -p "$OUTPUT_DIR"

for file in "$INPUT_DIR"/*.{mobi,epub,azw3}; do
    [ -f "$file" ] || continue
    filename=$(basename "$file")
    output="$OUTPUT_DIR/${filename%.*}.pdf"
    echo "转换: $filename"
    ebook-converter "$file" "$output"
done

echo "转换完成！"
```

## 🔍 故障排查

### 常见问题

**1. 服务无法启动**

```bash
# 检查端口占用
lsof -i :5001

# 强制停止
ebook-stop
pkill -9 -f "ebook_converter.web_app"

# 重新启动
ebook-convert
```

**2. 中文显示乱码**

```bash
# 检查字体安装
fc-list | grep -i kai

# 重新安装项目
pip uninstall ebook-converter
pip install .
```

**3. PDF 转换失败**

```bash
# 检查依赖
pip install --upgrade reportlab pillow

# 查看详细错误
tail -f /tmp/ebook_converter_web.log
```

**4. 文件名乱码**

确保：
- 使用最新版本的代码
- 浏览器支持 JavaScript
- 使用 Ctrl+F5 强制刷新浏览器

### 详细文档

- [快速开始指南](QUICKSTART.md)
- [Web 界面使用说明](WEB_INTERFACE.md)
- [故障排查](TROUBLESHOOTING.md)

## 🛠️ 开发

### 项目结构

```
ebook-converter/
├── ebook_converter/
│   ├── __init__.py
│   ├── main.py              # 命令行入口
│   ├── web_app.py           # Web 服务器
│   ├── pdf_converter.py     # PDF 转换核心
│   ├── templates/           # HTML 模板
│   │   ├── index.html       # 单文件转换
│   │   └── batch.html       # 批量转换
│   ├── ebooks/              # 格式转换器
│   │   ├── epub/
│   │   ├── mobi/
│   │   ├── pdf/
│   │   └── ...
│   └── utils/               # 工具函数
├── start.sh                 # 启动脚本
├── pyproject.toml           # 项目配置
└── README-CN.md             # 本文件
```

### 运行测试

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码风格检查
flake8 ebook_converter/
```

### 贡献代码

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📝 更新日志

### v1.1.0 (2025-11-08)

**新增功能**:
- ✨ 全新的 Web 界面（单文件和批量转换）
- ✨ PDF 输出支持（中文楷体字体）
- ✨ CSS 样式保留（颜色、对齐、缩进、字体）
- ✨ 中文文件名支持（使用 JavaScript 下载）
- ✨ 后台服务管理（ebook-convert、ebook-stop、ebook-status）
- ✨ 封面图片自动处理
- ✨ 章节自动分页

**改进**:
- 🔧 简化依赖关系
- 🔧 优化安装流程
- 📚 完善中英文文档
- 🐛 修复多个已知问题

### v1.0.0

- 🎉 初始版本
- 支持多种电子书格式转换
- 基于 Calibre 核心功能

## 📄 许可证

本项目采用 GPL-3.0 许可证，与原始 Calibre 项目保持一致。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [Calibre](https://calibre-ebook.com/) - 提供核心转换功能
- [ReportLab](https://www.reportlab.com/) - PDF 生成库
- [Flask](https://flask.palletsprojects.com/) - Web 框架
- 所有贡献者和用户

## 📮 联系方式

- 问题反馈: [GitHub Issues](https://github.com/why198546/ebook-converter/issues)
- Pull Request: [GitHub PR](https://github.com/why198546/ebook-converter/pulls)
- 原始项目: [gryf/ebook-converter](https://github.com/gryf/ebook-converter)

## 🌟 Star History

如果这个项目对您有帮助，请给我们一个 Star ⭐️！

---

**提示**: 本 README 完全基于当前代码功能编写。如发现任何问题或有改进建议，欢迎提交 Issue 或 PR。
