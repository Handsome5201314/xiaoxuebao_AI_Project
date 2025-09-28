#!/usr/bin/env python3
"""
测试运行脚本
提供不同类型的测试运行选项和报告生成
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Optional

def run_command(cmd: List[str], cwd: Optional[str] = None) -> int:
    """运行命令并返回退出码"""
    print(f"运行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    return result.returncode

def run_unit_tests(coverage: bool = True, verbose: bool = False) -> int:
    """运行单元测试"""
    print("🧪 运行单元测试...")
    
    cmd = ["python", "-m", "pytest"]
    
    if coverage:
        cmd.extend([
            "--cov=app",
            "--cov-report=html:htmlcov",
            "--cov-report=term-missing",
            "--cov-report=xml:coverage.xml"
        ])
    
    if verbose:
        cmd.append("-v")
    
    cmd.extend([
        "tests/test_*.py",
        "--tb=short"
    ])
    
    return run_command(cmd)

def run_integration_tests(verbose: bool = False) -> int:
    """运行集成测试"""
    print("🔗 运行集成测试...")
    
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    cmd.extend([
        "tests/integration/",
        "--tb=short",
        "-m", "integration"
    ])
    
    return run_command(cmd)

def run_api_tests(verbose: bool = False) -> int:
    """运行API测试"""
    print("🌐 运行API测试...")
    
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    cmd.extend([
        "tests/test_api_*.py",
        "--tb=short"
    ])
    
    return run_command(cmd)

def run_performance_tests(verbose: bool = False) -> int:
    """运行性能测试"""
    print("⚡ 运行性能测试...")
    
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    cmd.extend([
        "tests/",
        "--tb=short",
        "-m", "performance"
    ])
    
    return run_command(cmd)

def run_security_tests(verbose: bool = False) -> int:
    """运行安全测试"""
    print("🔒 运行安全测试...")
    
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    cmd.extend([
        "tests/",
        "--tb=short",
        "-m", "security"
    ])
    
    return run_command(cmd)

def run_linting() -> int:
    """运行代码检查"""
    print("🔍 运行代码检查...")
    
    exit_codes = []
    
    # Black格式检查
    print("检查代码格式 (Black)...")
    exit_codes.append(run_command(["black", "--check", "app/"]))
    
    # isort导入排序检查
    print("检查导入排序 (isort)...")
    exit_codes.append(run_command(["isort", "--check-only", "app/"]))
    
    # flake8代码风格检查
    print("检查代码风格 (flake8)...")
    exit_codes.append(run_command(["flake8", "app/"]))
    
    # mypy类型检查
    print("检查类型注解 (mypy)...")
    exit_codes.append(run_command(["mypy", "app/"]))
    
    return max(exit_codes) if exit_codes else 0

def run_security_scan() -> int:
    """运行安全扫描"""
    print("🛡️ 运行安全扫描...")
    
    exit_codes = []
    
    # bandit安全检查
    print("运行安全检查 (bandit)...")
    exit_codes.append(run_command([
        "bandit", "-r", "app/", 
        "-f", "json", 
        "-o", "bandit-report.json"
    ]))
    
    # safety依赖安全检查
    print("检查依赖安全性 (safety)...")
    exit_codes.append(run_command(["safety", "check", "--json", "--output", "safety-report.json"]))
    
    return max(exit_codes) if exit_codes else 0

def generate_test_report() -> None:
    """生成测试报告"""
    print("📊 生成测试报告...")
    
    # 生成HTML覆盖率报告
    if os.path.exists("htmlcov/index.html"):
        print("✅ HTML覆盖率报告已生成: htmlcov/index.html")
    
    # 生成JUnit XML报告
    run_command([
        "python", "-m", "pytest", 
        "--junitxml=test-results.xml",
        "tests/"
    ])
    
    print("✅ JUnit XML报告已生成: test-results.xml")

def setup_test_environment() -> None:
    """设置测试环境"""
    print("🔧 设置测试环境...")
    
    # 设置环境变量
    os.environ["TESTING"] = "1"
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_xiaoxuebao.db"
    os.environ["REDIS_URL"] = "redis://localhost:6379/1"
    
    # 创建测试目录
    test_dirs = ["htmlcov", "test-reports"]
    for dir_name in test_dirs:
        Path(dir_name).mkdir(exist_ok=True)
    
    print("✅ 测试环境设置完成")

def cleanup_test_environment() -> None:
    """清理测试环境"""
    print("🧹 清理测试环境...")
    
    # 删除测试数据库
    test_db_files = ["test_xiaoxuebao.db", "test_xiaoxuebao.db-shm", "test_xiaoxuebao.db-wal"]
    for db_file in test_db_files:
        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"删除测试数据库文件: {db_file}")
    
    print("✅ 测试环境清理完成")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="小雪宝项目测试运行器")
    parser.add_argument("--type", choices=["unit", "integration", "api", "performance", "security", "all"], 
                       default="all", help="测试类型")
    parser.add_argument("--coverage", action="store_true", default=True, help="生成覆盖率报告")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--lint", action="store_true", help="运行代码检查")
    parser.add_argument("--security-scan", action="store_true", help="运行安全扫描")
    parser.add_argument("--report", action="store_true", help="生成测试报告")
    parser.add_argument("--cleanup", action="store_true", help="清理测试环境")
    
    args = parser.parse_args()
    
    # 设置测试环境
    setup_test_environment()
    
    exit_code = 0
    
    try:
        # 运行代码检查
        if args.lint:
            lint_code = run_linting()
            if lint_code != 0:
                print("❌ 代码检查失败")
                exit_code = max(exit_code, lint_code)
        
        # 运行安全扫描
        if args.security_scan:
            security_code = run_security_scan()
            if security_code != 0:
                print("❌ 安全扫描发现问题")
                exit_code = max(exit_code, security_code)
        
        # 运行测试
        if args.type == "unit" or args.type == "all":
            unit_code = run_unit_tests(coverage=args.coverage, verbose=args.verbose)
            if unit_code != 0:
                print("❌ 单元测试失败")
                exit_code = max(exit_code, unit_code)
        
        if args.type == "integration" or args.type == "all":
            integration_code = run_integration_tests(verbose=args.verbose)
            if integration_code != 0:
                print("❌ 集成测试失败")
                exit_code = max(exit_code, integration_code)
        
        if args.type == "api" or args.type == "all":
            api_code = run_api_tests(verbose=args.verbose)
            if api_code != 0:
                print("❌ API测试失败")
                exit_code = max(exit_code, api_code)
        
        if args.type == "performance":
            perf_code = run_performance_tests(verbose=args.verbose)
            if perf_code != 0:
                print("❌ 性能测试失败")
                exit_code = max(exit_code, perf_code)
        
        if args.type == "security":
            sec_code = run_security_tests(verbose=args.verbose)
            if sec_code != 0:
                print("❌ 安全测试失败")
                exit_code = max(exit_code, sec_code)
        
        # 生成报告
        if args.report:
            generate_test_report()
        
        if exit_code == 0:
            print("✅ 所有测试通过!")
        else:
            print("❌ 部分测试失败")
    
    finally:
        # 清理测试环境
        if args.cleanup:
            cleanup_test_environment()
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
