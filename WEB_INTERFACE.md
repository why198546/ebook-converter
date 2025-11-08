# Ebook Converter Web 界面使用说明

## 概述

Ebook Converter 现在提供了两种使用方式：
1. **命令行模式** - 适合批量处理和脚本自动化
2. **Web 界面模式** - 提供可视化操作界面，更加友好

## 安装

确保你已经按照主 README.rst 中的说明安装了项目。如果还没有，请执行：

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 安装项目及依赖（包括 Flask）
pip install .
```

## 使用方法

### 方式一：命令行模式（原有功能保留）

适合批量转换和脚本自动化：

```bash
# 激活虚拟环境
source venv/bin/activate

# 转换单个文件
ebook-converter input.epub output.mobi

# 批量转换（使用 shell 脚本）
for file in *.epub; do
    ebook-converter "$file" "${file%.epub}.mobi"
done
```

### 方式二：Web 界面模式（新增功能）

适合需要可视化操作的场景：

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动 Web 服务器
ebook-converter-web
# 或者
python -m ebook_converter.web_app
```

启动后，在浏览器中访问：`http://127.0.0.1:5001`

## Web 界面功能

### 1. 单文件转换
- 访问首页 (http://127.0.0.1:5001)
- 点击或拖拽文件到上传区域
- 选择目标输出格式
- 点击"开始转换"按钮
- 转换完成后自动下载结果文件

### 2. 批量转换
- 访问批量转换页面 (http://127.0.0.1:5001/batch)
- 选择多个文件（可以点击或拖拽）
- 选择统一的输出格式
- 点击"开始批量转换"按钮
- 查看每个文件的转换结果

## 支持的格式

### 输入格式
- DOCX (Microsoft Word 2007+)
- EPUB (v2 和 v3)
- ODT (LibreOffice)
- TXT (纯文本)
- PDB (PalmOS 格式)
- RTF (富文本格式)
- MOBI (Mobipocket)
- AZW3/AZW4 (Kindle)
- FB2 (FictionBook)
- HTML/HTM
- PDF
- LRF (Broadband eBook)

### 输出格式
- LRF (Broadband eBook)
- EPUB (v2)
- MOBI (Mobipocket)
- DOCX (Microsoft Word)
- HTMLZ (压缩的 HTML)
- TXT (纯文本)

## 限制

- 单个文件最大大小：100MB
- Web 界面仅用于开发和个人使用
- 生产环境建议使用专业的 WSGI 服务器（如 Gunicorn）

## 故障排除

### 端口被占用
如果 5001 端口被占用，可以编辑 `ebook_converter/web_app.py` 修改端口号：

```python
app.run(debug=True, host='0.0.0.0', port=5002)  # 改为其他端口
```

### 转换失败
- 检查输入文件是否损坏
- 确认文件格式确实被支持
- 查看终端输出的错误信息
- 尝试使用命令行模式获取更详细的错误信息

## 技术栈

- **后端**: Flask (Python Web 框架)
- **前端**: 原生 HTML/CSS/JavaScript
- **转换引擎**: ebook-converter (基于 Calibre)

## 开发说明

如果你想修改 Web 界面：

- HTML 模板位于: `ebook_converter/templates/`
- 静态文件位于: `ebook_converter/static/`
- Flask 应用代码: `ebook_converter/web_app.py`

修改后无需重启服务器（Debug 模式会自动重载）。

## 安全提示

**重要**: 此 Web 界面使用 Flask 的开发服务器，仅适用于本地开发和个人使用。

如果需要在生产环境部署，请：
1. 使用 Gunicorn 或 uWSGI 等生产级 WSGI 服务器
2. 配置 Nginx 或 Apache 作为反向代理
3. 启用 HTTPS
4. 实施适当的访问控制和安全措施

## 贡献

欢迎提交 Issues 和 Pull Requests！

## 许可证

与主项目相同，采用 GPL-3.0-or-later 许可证。
