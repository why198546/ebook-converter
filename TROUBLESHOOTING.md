# 故障排除指南

## 常见问题及解决方案

### 1. libxml2 版本冲突错误

**错误信息：**
```
RuntimeError: html5-parser and lxml are using different versions of libxml2. 
This happens commonly when using pip installed versions of lxml. 
Use pip install --no-binary lxml lxml instead. 
libxml2 versions: html5-parser: (2, 13, 8) != lxml: (2, 14, 6)
```

**原因：**
html5-parser 和 lxml 使用了不同版本的 libxml2 库，导致冲突。

**解决方法：**
```bash
# 激活虚拟环境
source venv/bin/activate

# 卸载现有的 lxml
pip uninstall -y lxml

# 从源代码重新安装 lxml（不使用预编译的二进制文件）
pip install --no-binary lxml lxml
```

这样可以确保 lxml 使用与 html5-parser 相同的系统 libxml2 库。

### 2. 端口被占用

**错误信息：**
```
Address already in use
Port 5000 is in use by another program
```

**解决方法：**
已经将默认端口改为 5001。如果仍然冲突，编辑 `ebook_converter/web_app.py`：

```python
# 在文件末尾修改端口号
app.run(debug=True, host='0.0.0.0', port=5002)  # 改为其他可用端口
```

### 3. 转换失败（500 错误）

**可能原因：**
- 文件格式不支持
- 文件损坏
- 依赖库问题（特别是 libxml2 冲突）

**排查步骤：**

1. **先用命令行测试：**
```bash
source venv/bin/activate
ebook-converter input_file.txt output_file.epub
```

2. **检查详细错误信息：**
查看终端窗口的输出，Web 服务器会打印详细的错误堆栈。

3. **确认文件格式：**
确保输入文件格式在支持列表中（查看 Web 界面提示）。

### 4. pkg_resources 废弃警告

**警告信息：**
```
UserWarning: pkg_resources is deprecated as an API
```

**说明：**
这只是一个警告，不影响功能。这是上游 Calibre 代码的问题，将在未来版本中修复。

**临时忽略方法：**
这个警告不影响使用，可以安全忽略。

### 5. 文件下载失败

**症状：**
转换成功但无法下载文件。

**原因：**
临时文件在发送前被删除。

**解决方法：**
已在代码中修复，现在文件会先读取到内存，然后通过 BytesIO 发送。

### 6. 批量转换部分失败

**症状：**
批量转换时某些文件成功，某些失败。

**原因：**
- 个别文件格式问题
- 文件损坏
- 格式转换不兼容

**建议：**
- 查看转换结果中的错误信息
- 将失败的文件单独用命令行工具测试
- 确认输入输出格式兼容性

## 性能优化建议

### 大文件转换

对于大型电子书文件（>50MB）：
1. 使用命令行模式可能更稳定
2. 确保有足够的磁盘空间
3. 转换可能需要几分钟时间

### 批量转换优化

```bash
# 使用命令行批量转换更高效
for file in *.epub; do
    ebook-converter "$file" "${file%.epub}.mobi"
done
```

## 获取帮助

如果遇到其他问题：

1. 查看终端输出的详细错误信息
2. 确认已安装所有系统依赖（Liberation Fonts, Poppler）
3. 确认虚拟环境已正确激活
4. 尝试使用命令行模式进行调试

## 成功安装的验证

运行以下命令验证安装：

```bash
# 激活虚拟环境
source venv/bin/activate

# 测试命令行转换
echo "测试内容" > test.txt
ebook-converter test.txt test.epub

# 启动 Web 界面
ebook-converter-web

# 在浏览器访问
open http://127.0.0.1:5001
```

如果以上都成功，说明安装正确。
