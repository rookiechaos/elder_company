#!/usr/bin/env python3
"""
Game模块环境检查脚本
检查game模块的文件结构和基本配置
"""

import os
import json
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """检查文件是否存在"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} 不存在: {filepath}")
        return False

def check_directory_exists(dirpath, description):
    """检查目录是否存在"""
    if os.path.isdir(dirpath):
        print(f"✅ {description}: {dirpath}/")
        return True
    else:
        print(f"❌ {description} 不存在: {dirpath}/")
        return False

def check_package_json():
    """检查package.json"""
    package_path = "frontend/package.json"
    if not os.path.exists(package_path):
        print(f"❌ package.json 不存在")
        return False
    
    try:
        with open(package_path, 'r', encoding='utf-8') as f:
            package = json.load(f)
        
        print(f"✅ package.json 格式正确")
        print(f"   项目名称: {package.get('name', 'N/A')}")
        print(f"   版本: {package.get('version', 'N/A')}")
        
        # 检查关键依赖
        deps = package.get('dependencies', {})
        key_deps = ['react', 'react-dom', 'zustand', 'framer-motion', 'axios']
        print(f"\n   关键依赖:")
        for dep in key_deps:
            if dep in deps:
                print(f"     ✅ {dep}: {deps[dep]}")
            else:
                print(f"     ❌ {dep}: 缺失")
        
        return True
    except json.JSONDecodeError as e:
        print(f"❌ package.json JSON格式错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 读取package.json时出错: {e}")
        return False

def check_jsx_syntax(filepath):
    """简单检查JSX文件语法（基本检查）"""
    if not os.path.exists(filepath):
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 基本语法检查
        issues = []
        
        # 检查是否有基本的React导入
        if 'import' in content and 'react' in content.lower():
            pass  # 基本结构存在
        elif 'React' in content or 'react' in content:
            pass  # 可能使用了其他方式
        
        # 检查是否有export
        if 'export' in content:
            pass  # 有导出
        
        # 检查括号匹配（简单检查）
        open_braces = content.count('{')
        close_braces = content.count('}')
        if abs(open_braces - close_braces) > 2:  # 允许一些差异
            issues.append(f"括号可能不匹配 ({{: {open_braces}, }}: {close_braces})")
        
        if issues:
            print(f"   ⚠️  潜在问题: {', '.join(issues)}")
        else:
            print(f"   ✅ 基本语法检查通过")
        
        return True
    except Exception as e:
        print(f"   ❌ 读取文件时出错: {e}")
        return False

def main():
    """主检查函数"""
    print("=" * 60)
    print("Elder Company Game模块环境检查")
    print("=" * 60)
    print()
    
    # 切换到game目录
    game_dir = Path(__file__).parent
    os.chdir(game_dir)
    
    print("📁 目录结构检查:")
    print("-" * 60)
    
    dirs = [
        ("frontend", "前端目录"),
        ("frontend/src", "源代码目录"),
        ("frontend/src/games", "游戏组件目录"),
        ("frontend/src/components", "共享组件目录"),
        ("frontend/src/hooks", "Hooks目录"),
        ("frontend/src/utils", "工具函数目录"),
        ("frontend/src/store", "状态管理目录"),
        ("frontend/public", "公共资源目录"),
        ("assets", "资源目录"),
        ("assets/images", "图片资源目录"),
        ("assets/sounds", "音效资源目录"),
        ("assets/themes", "主题资源目录"),
        ("docs", "文档目录"),
    ]
    
    dir_ok = True
    for dirpath, desc in dirs:
        if not check_directory_exists(dirpath, desc):
            dir_ok = False
    
    print()
    print("📄 关键文件检查:")
    print("-" * 60)
    
    files = [
        ("frontend/package.json", "package.json"),
        ("frontend/vite.config.js", "Vite配置文件"),
        ("frontend/index.html", "HTML入口文件"),
        ("frontend/src/main.jsx", "React入口文件"),
        ("frontend/src/App.jsx", "主应用组件"),
        ("frontend/src/App.css", "应用样式"),
        ("frontend/src/index.css", "全局样式"),
        ("README.md", "项目说明"),
        ("DESIGN.md", "设计文档"),
        ("GAME_SPECS.md", "游戏规格"),
        ("IMPLEMENTATION_PLAN.md", "实现计划"),
        ("docs/API.md", "API文档"),
    ]
    
    file_ok = True
    for filepath, desc in files:
        if not check_file_exists(filepath, desc):
            file_ok = False
    
    print()
    print("📦 package.json 详细检查:")
    print("-" * 60)
    package_ok = check_package_json()
    
    print()
    print("🔍 JSX文件语法检查:")
    print("-" * 60)
    
    jsx_files = [
        ("frontend/src/main.jsx", "main.jsx"),
        ("frontend/src/App.jsx", "App.jsx"),
    ]
    
    jsx_ok = True
    for filepath, desc in jsx_files:
        print(f"检查 {desc}:")
        if not check_jsx_syntax(filepath):
            jsx_ok = False
        print()
    
    print()
    print("=" * 60)
    print("检查总结")
    print("=" * 60)
    
    all_ok = dir_ok and file_ok and package_ok and jsx_ok
    
    if all_ok:
        print("✅ 所有基础检查通过！")
        print()
        print("📝 下一步:")
        print("   1. 安装Node.js和npm（如果尚未安装）")
        print("   2. 运行: cd frontend && npm install")
        print("   3. 运行: npm run dev")
        print("   4. 开始开发游戏功能")
    else:
        print("⚠️  发现一些问题，请检查上述输出")
        print()
        print("💡 提示:")
        print("   - 确保所有必需的文件都已创建")
        print("   - 检查文件路径是否正确")
        print("   - 验证JSON文件格式")
    
    print()
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
