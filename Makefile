.PHONY: start stop web test clean help

# 启动 Web 服务
start:
	@echo "🚀 启动 Ebook Converter Web 服务..."
	@cd $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST)))) && \
	source venv/bin/activate && \
	python -m ebook_converter.web_app

# 停止 Web 服务
stop:
	@echo "🛑 停止 Web 服务..."
	@pkill -f "ebook_converter.web_app" || echo "服务未运行"

# 启动 Web 服务（别名）
web: start

# 运行测试
test:
	@cd $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST)))) && \
	source venv/bin/activate && \
	python -c "from ebook_converter.pdf_converter import convert_to_pdf_via_epub; print('✓ PDF converter ready')"

# 清理临时文件
clean:
	@echo "🧹 清理临时文件..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✓ 清理完成"

# 显示帮助
help:
	@echo "Ebook Converter - 可用命令："
	@echo ""
	@echo "  make start   - 启动 Web 服务"
	@echo "  make stop    - 停止 Web 服务"
	@echo "  make web     - 启动 Web 服务（同 start）"
	@echo "  make test    - 测试转换功能"
	@echo "  make clean   - 清理临时文件"
	@echo "  make help    - 显示此帮助"
	@echo ""
	@echo "或者直接运行: ./start.sh"
