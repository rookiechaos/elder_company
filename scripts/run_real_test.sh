#!/bin/bash
# 真实API测试脚本启动器

echo "=========================================="
echo "Elder Company - 真实API测试"
echo "=========================================="
echo ""

# 检查服务器是否运行
echo "检查服务器状态..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 服务器正在运行"
    echo ""
    echo "开始运行测试..."
    echo ""
    python3 test_real_api.py --url http://localhost:8000
else
    echo "❌ 服务器未运行"
    echo ""
    echo "请先启动服务器:"
    echo "  cd backend"
    echo "  uvicorn main:app --reload"
    echo ""
    echo "或者使用以下命令在后台启动:"
    echo "  nohup uvicorn main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &"
    echo ""
    read -p "是否现在启动服务器? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "启动服务器..."
        uvicorn main:app --host 0.0.0.0 --port 8000 &
        SERVER_PID=$!
        echo "服务器PID: $SERVER_PID"
        echo "等待服务器启动..."
        sleep 5
        
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo "✅ 服务器启动成功"
            echo ""
            echo "开始运行测试..."
            echo ""
            python3 test_real_api.py --url http://localhost:8000
            echo ""
            echo "停止服务器..."
            kill $SERVER_PID
        else
            echo "❌ 服务器启动失败，请检查日志"
            kill $SERVER_PID 2>/dev/null
        fi
    fi
fi
