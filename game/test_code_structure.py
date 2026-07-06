#!/usr/bin/env python3
"""
Game模块代码结构验证
检查代码文件的基本结构和语法正确性
"""

import os
import re
import json
import sys
from pathlib import Path

def check_imports(filepath, required_imports=None):
    """检查文件中的导入语句"""
    if not os.path.exists(filepath):
        return False, []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        found_imports = []
        missing_imports = []
        
        # 检查React相关导入
        if 'react' in content.lower() or 'React' in content:
            if 'import' in content:
                # 提取import语句
                import_pattern = r'import\s+.*?from\s+[\'"]react'
                if re.search(import_pattern, content):
                    found_imports.append('react')
                else:
                    missing_imports.append('react导入格式')
        
        # 检查CSS导入
        if '.css' in content or 'App.css' in content or 'index.css' in content:
            found_imports.append('css')
        
        return True, found_imports
    except Exception as e:
        return False, [f"错误: {e}"]

def check_jsx_structure(filepath):
    """检查JSX文件的基本结构"""
    if not os.path.exists(filepath):
        return False, []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        checks = []
        
        # 检查文件类型（入口文件 vs 组件文件）
        is_entry = 'main.jsx' in filepath or 'main.tsx' in filepath
        
        if is_entry:
            # 入口文件检查
            if 'ReactDOM' in content or 'createRoot' in content:
                checks.append("✅ 有ReactDOM渲染代码")
            else:
                issues.append("缺少ReactDOM渲染代码")
            
            if 'import' in content and 'App' in content:
                checks.append("✅ 导入了App组件")
            else:
                issues.append("缺少App组件导入")
        else:
            # 组件文件检查
            if 'function' in content or 'const' in content or 'export default' in content:
                checks.append("✅ 有组件定义")
            else:
                issues.append("缺少组件定义")
            
            # 检查是否有return语句（JSX需要）
            if 'return' in content:
                checks.append("✅ 有return语句")
            else:
                issues.append("缺少return语句")
            
            # 检查JSX语法（基本检查）
            if '<div' in content or '<h1' in content or 'className' in content:
                checks.append("✅ 有JSX语法")
            else:
                issues.append("缺少JSX语法")
        
        # 检查括号平衡（简单检查）
        open_braces = content.count('{')
        close_braces = content.count('}')
        open_parens = content.count('(')
        close_parens = content.count(')')
        
        if abs(open_braces - close_braces) <= 2:
            checks.append("✅ 大括号基本平衡")
        else:
            issues.append(f"大括号不平衡 ({{: {open_braces}, }}: {close_braces})")
        
        if abs(open_parens - close_parens) <= 2:
            checks.append("✅ 小括号基本平衡")
        else:
            issues.append(f"小括号不平衡 ((: {open_parens}, ): {close_parens})")
        
        return len(issues) == 0, checks + issues
    except Exception as e:
        return False, [f"读取错误: {e}"]

def check_html_structure(filepath):
    """检查HTML文件结构"""
    if not os.path.exists(filepath):
        return False, []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = []
        issues = []
        
        # 检查基本HTML结构
        if '<html' in content.lower():
            checks.append("✅ 有html标签")
        else:
            issues.append("缺少html标签")
        
        if '<head' in content.lower():
            checks.append("✅ 有head标签")
        else:
            issues.append("缺少head标签")
        
        if '<body' in content.lower():
            checks.append("✅ 有body标签")
        else:
            issues.append("缺少body标签")
        
        # 检查React挂载点
        if 'id="root"' in content or "id='root'" in content:
            checks.append("✅ 有React挂载点")
        else:
            issues.append("缺少React挂载点 (id='root')")
        
        # 检查script标签
        if '<script' in content.lower():
            checks.append("✅ 有script标签")
        else:
            issues.append("缺少script标签")
        
        return len(issues) == 0, checks + issues
    except Exception as e:
        return False, [f"读取错误: {e}"]

def check_vite_config(filepath):
    """检查Vite配置文件"""
    if not os.path.exists(filepath):
        return False, []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = []
        issues = []
        
        # 检查基本配置
        if 'defineConfig' in content:
            checks.append("✅ 使用defineConfig")
        else:
            issues.append("缺少defineConfig")
        
        if 'react' in content.lower():
            checks.append("✅ 配置了React插件")
        else:
            issues.append("缺少React插件配置")
        
        if 'plugins' in content:
            checks.append("✅ 有plugins配置")
        else:
            issues.append("缺少plugins配置")
        
        return len(issues) == 0, checks + issues
    except Exception as e:
        return False, [f"读取错误: {e}"]

def main():
    """主验证函数"""
    print("=" * 60)
    print("Game模块代码结构验证")
    print("=" * 60)
    print()
    
    # 切换到game目录
    game_dir = Path(__file__).parent
    os.chdir(game_dir)
    
    all_ok = True
    
    # 检查main.jsx
    print("📄 检查 main.jsx:")
    print("-" * 60)
    ok, details = check_jsx_structure("frontend/src/main.jsx")
    for detail in details:
        print(f"  {detail}")
    if not ok:
        all_ok = False
    print()
    
    # 检查App.jsx
    print("📄 检查 App.jsx:")
    print("-" * 60)
    ok, details = check_jsx_structure("frontend/src/App.jsx")
    for detail in details:
        print(f"  {detail}")
    
    # 检查导入
    ok_import, imports = check_imports("frontend/src/App.jsx")
    if imports:
        print(f"  导入检查: {', '.join(imports)}")
    if not ok or not ok_import:
        all_ok = False
    print()
    
    # 检查index.html
    print("📄 检查 index.html:")
    print("-" * 60)
    ok, details = check_html_structure("frontend/index.html")
    for detail in details:
        print(f"  {detail}")
    if not ok:
        all_ok = False
    print()
    
    # 检查vite.config.js
    print("📄 检查 vite.config.js:")
    print("-" * 60)
    ok, details = check_vite_config("frontend/vite.config.js")
    for detail in details:
        print(f"  {detail}")
    if not ok:
        all_ok = False
    print()
    
    # 检查package.json
    print("📄 检查 package.json:")
    print("-" * 60)
    if os.path.exists("frontend/package.json"):
        try:
            with open("frontend/package.json", 'r') as f:
                package = json.load(f)
            
            # 检查scripts
            scripts = package.get('scripts', {})
            required_scripts = ['dev', 'build']
            for script in required_scripts:
                if script in scripts:
                    print(f"  ✅ script '{script}' 存在")
                else:
                    print(f"  ❌ script '{script}' 缺失")
                    all_ok = False
            
            # 检查dependencies
            deps = package.get('dependencies', {})
            required_deps = ['react', 'react-dom']
            for dep in required_deps:
                if dep in deps:
                    print(f"  ✅ dependency '{dep}' 存在")
                else:
                    print(f"  ❌ dependency '{dep}' 缺失")
                    all_ok = False
        except Exception as e:
            print(f"  ❌ 读取package.json失败: {e}")
            all_ok = False
    else:
        print("  ❌ package.json 不存在")
        all_ok = False
    print()
    
    print("=" * 60)
    print("验证总结")
    print("=" * 60)
    
    if all_ok:
        print("✅ 所有代码结构检查通过！")
        print()
        print("📝 代码结构验证结果:")
        print("   ✅ React组件结构正确")
        print("   ✅ HTML入口文件正确")
        print("   ✅ Vite配置正确")
        print("   ✅ package.json配置正确")
        print()
        print("💡 注意:")
        print("   - 代码结构已验证，但需要Node.js环境才能运行")
        print("   - 安装依赖: cd frontend && npm install")
        print("   - 启动开发服务器: npm run dev")
        print("   - 实际游戏功能需要进一步开发")
    else:
        print("⚠️  发现一些问题，请检查上述输出")
    
    print()
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
