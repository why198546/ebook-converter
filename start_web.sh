#!/usr/bin/env bash
# Ebook Converter Web 界面启动脚本

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 激活虚拟环境
if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
    echo "✓ 虚拟环境已激活"
else
    echo "✗ 错误：未找到虚拟环境"
    echo "请先运行: python3 -m venv venv && source venv/bin/activate && pip install ."
    exit 1
fi

# 检查 Flask 是否已安装
if ! python -c "import flask" 2>/dev/null; then
    echo "✗ Flask 未安装"
    echo "正在安装 Flask..."
    pip install flask
fi

# 启动 Web 服务器
echo ""
echo "=========================================="
echo "  📚 Ebook Converter Web 界面"
echo "=========================================="
echo ""
echo "正在启动 Web 服务器..."
echo "请在浏览器中访问: http://127.0.0.1:5001"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

python -m ebook_converter.web_app
