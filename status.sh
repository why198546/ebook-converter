#!/bin/bash

# 检查服务状态
if pgrep -f "ebook_converter.web_app" > /dev/null; then
    PID=$(pgrep -f "ebook_converter.web_app" | head -1)
    echo "✓ 服务正在运行"
    echo "  PID: $PID"
    echo "  URL: http://127.0.0.1:5001"
    echo "  日志: /tmp/ebook_converter_web.log"
    echo ""
    echo "最近的日志:"
    tail -10 /tmp/ebook_converter_web.log 2>/dev/null || echo "  无日志文件"
else
    echo "✗ 服务未运行"
    echo "使用 'ebook-convert' 命令启动服务"
fi
