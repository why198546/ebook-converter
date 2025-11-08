#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate

URL="http://127.0.0.1:5001"
LOG_FILE="/tmp/ebook_converter_web.log"

# 检查服务是否已在运行
if pgrep -f "ebook_converter.web_app" > /dev/null; then
    echo "✓ 服务已在运行"
    
    # 使用 AppleScript 激活或打开浏览器标签
    osascript -e "
    on run
        set targetURL to \"$URL\"
        set found to false
        
        -- 尝试 Safari
        tell application \"Safari\"
            if it is running then
                repeat with w in windows
                    set tabIndex to 0
                    repeat with t in tabs of w
                        set tabIndex to tabIndex + 1
                        if URL of t contains \"127.0.0.1:5001\" then
                            set current tab of w to t
                            set index of w to 1
                            activate
                            set found to true
                            exit repeat
                        end if
                    end repeat
                    if found then exit repeat
                end repeat
            end if
        end tell
        
        -- 如果 Safari 没找到，尝试 Chrome
        if not found then
            tell application \"System Events\"
                set chromeRunning to (name of processes) contains \"Google Chrome\"
            end tell
            
            if chromeRunning then
                tell application \"Google Chrome\"
                    repeat with w in windows
                        set tabIndex to 0
                        repeat with t in tabs of w
                            set tabIndex to tabIndex + 1
                            if URL of t contains \"127.0.0.1:5001\" then
                                tell w to set active tab index to tabIndex
                                set index of w to 1
                                activate
                                set found to true
                                exit repeat
                            end if
                        end repeat
                        if found then exit repeat
                    end repeat
                end tell
            end if
        end if
        
        -- 如果没找到已打开的标签，打开新标签
        if not found then
            do shell script \"open \" & quoted form of targetURL
        end if
    end run
    " 2>/dev/null || open "$URL"
    
    echo "🌐 已切换到浏览器页面"
else
    echo "🚀 启动服务..."
    
    # 使用 nohup 在后台启动服务器，输出到日志文件
    nohup python -m ebook_converter.web_app > "$LOG_FILE" 2>&1 &
    SERVER_PID=$!
    
    # 等待服务器启动
    echo "⏳ 等待服务器启动..."
    sleep 3
    
    # 检查服务是否成功启动
    if ps -p $SERVER_PID > /dev/null; then
        echo "✓ 服务已启动 (PID: $SERVER_PID)"
        echo "📝 日志文件: $LOG_FILE"
        echo "🌐 访问地址: $URL"
        
        # 打开浏览器
        open "$URL"
        
        echo ""
        echo "提示: 使用 'ebook-stop' 命令停止服务"
    else
        echo "✗ 服务启动失败，请查看日志: $LOG_FILE"
        exit 1
    fi
fi
