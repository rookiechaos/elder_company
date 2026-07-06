#!/bin/bash
# Redis Setup Script for Elder Company
# Redis 设置脚本

set -e

echo "🚀 Elder Company - Redis 设置脚本"
echo "=================================="
echo ""

# Check if Redis is installed
if ! command -v redis-server &> /dev/null; then
    echo "❌ Redis 未安装"
    echo ""
    echo "请先安装 Redis:"
    echo ""
    echo "macOS:"
    echo "  brew install redis"
    echo ""
    echo "Ubuntu/Debian:"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install redis-server"
    echo ""
    echo "CentOS/RHEL:"
    echo "  sudo yum install redis"
    echo ""
    echo "Docker:"
    echo "  docker run -d -p 6379:6379 --name redis redis:latest"
    echo ""
    exit 1
fi

echo "✅ Redis 已安装"
echo ""

# Check if Redis is running
if redis-cli ping &> /dev/null; then
    echo "✅ Redis 服务正在运行"
else
    echo "⚠️  Redis 服务未运行，正在启动..."
    
    # Try to start Redis
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew services start redis
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo systemctl start redis
        sudo systemctl enable redis
    fi
    
    sleep 2
    
    if redis-cli ping &> /dev/null; then
        echo "✅ Redis 服务已启动"
    else
        echo "❌ 无法启动 Redis 服务"
        echo "请手动启动 Redis:"
        echo "  redis-server"
        exit 1
    fi
fi

echo ""
echo "📝 配置信息:"
echo "  Redis Host: localhost"
echo "  Redis Port: 6379"
echo "  Redis URL: redis://localhost:6379/0"
echo ""

# Test Redis connection
echo "🧪 测试 Redis 连接..."
if redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis 连接测试成功"
else
    echo "❌ Redis 连接测试失败"
    exit 1
fi

echo ""
echo "📋 下一步操作:"
echo "1. 在 backend/.env 文件中添加:"
echo "   REDIS_URL=redis://localhost:6379/0"
echo ""
echo "2. 重启后端服务以应用配置"
echo ""
echo "3. 运行测试脚本验证分布式限流:"
echo "   python scripts/test_redis_rate_limit.py"
echo ""
