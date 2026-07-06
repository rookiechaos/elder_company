#!/usr/bin/env python3
"""
Elder Company - 压力测试脚本

测试API在高负载下的性能和稳定性
"""

import asyncio
import aiohttp
import time
import argparse
import statistics
from typing import List, Dict, Any
from collections import defaultdict
import json
from datetime import datetime

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_info(msg: str):
    print(f"{Colors.CYAN}ℹ️  {msg}{Colors.RESET}")

def print_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def print_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")

def print_header(msg: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{msg}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")

class StressTestResult:
    """压力测试结果"""
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.response_times: List[float] = []
        self.errors: Dict[str, int] = defaultdict(int)
        self.status_codes: Dict[int, int] = defaultdict(int)
        self.start_time = None
        self.end_time = None

    def add_result(self, success: bool, response_time: float, status_code: int = None, error: str = None):
        self.total_requests += 1
        if success:
            self.successful_requests += 1
            self.response_times.append(response_time)
            if status_code:
                self.status_codes[status_code] += 1
        else:
            self.failed_requests += 1
            if error:
                self.errors[error] += 1
            if status_code:
                self.status_codes[status_code] += 1

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        duration = (self.end_time - self.start_time) if self.end_time and self.start_time else 0
        
        if not self.response_times:
            return {
                "total": self.total_requests,
                "total_requests": self.total_requests,
                "success": self.successful_requests,
                "successful_requests": self.successful_requests,
                "failed": self.failed_requests,
                "failed_requests": self.failed_requests,
                "success_rate": (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0.0,
                "error_rate": (self.failed_requests / self.total_requests * 100) if self.total_requests > 0 else 0.0,
                "avg_response_time": 0,
                "median_response_time": 0,
                "p95_response_time": 0,
                "p99_response_time": 0,
                "min_response_time": 0,
                "max_response_time": 0,
                "qps": self.total_requests / duration if duration > 0 else 0,
                "duration": duration,
                "status_codes": dict(self.status_codes),
                "errors": dict(self.errors)
            }

        sorted_times = sorted(self.response_times)
        duration = (self.end_time - self.start_time) if self.end_time and self.start_time else 0

        return {
            "total": self.total_requests,
            "total_requests": self.total_requests,
            "success": self.successful_requests,
            "successful_requests": self.successful_requests,
            "failed": self.failed_requests,
            "failed_requests": self.failed_requests,
            "success_rate": (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0,
            "error_rate": (self.failed_requests / self.total_requests * 100) if self.total_requests > 0 else 0,
            "avg_response_time": statistics.mean(self.response_times) if self.response_times else 0,
            "median_response_time": statistics.median(self.response_times) if self.response_times else 0,
            "p95_response_time": sorted_times[int(len(sorted_times) * 0.95)] if sorted_times else 0,
            "p99_response_time": sorted_times[int(len(sorted_times) * 0.99)] if sorted_times else 0,
            "min_response_time": min(self.response_times) if self.response_times else 0,
            "max_response_time": max(self.response_times) if self.response_times else 0,
            "qps": self.total_requests / duration if duration > 0 else 0,
            "duration": duration,
            "status_codes": dict(self.status_codes),
            "errors": dict(self.errors)
        }

async def make_request(session: aiohttp.ClientSession, url: str, method: str = "GET", 
                      data: Dict = None, timeout: int = 30) -> tuple:
    """发送单个请求"""
    start_time = time.time()
    try:
        if method == "GET":
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                response_time = (time.time() - start_time) * 1000  # 转换为毫秒
                text = await response.text()
                return (True, response_time, response.status, None)
        elif method == "POST":
            async with session.post(url, json=data, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                response_time = (time.time() - start_time) * 1000
                text = await response.text()
                return (True, response_time, response.status, None)
    except asyncio.TimeoutError:
        response_time = (time.time() - start_time) * 1000
        return (False, response_time, None, "Timeout")
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        return (False, response_time, None, str(e))

async def run_stress_test(base_url: str, endpoint: str, concurrent: int, 
                         total_requests: int, method: str = "GET", 
                         request_data: Dict = None, timeout: int = 30) -> StressTestResult:
    """运行压力测试"""
    result = StressTestResult()
    result.start_time = time.time()
    
    url = f"{base_url}{endpoint}"
    print_info(f"测试端点: {url}")
    print_info(f"并发数: {concurrent}, 总请求数: {total_requests}")
    
    semaphore = asyncio.Semaphore(concurrent)
    completed = 0
    lock = asyncio.Lock()
    
    async def worker():
        nonlocal completed
        async with aiohttp.ClientSession() as session:
            while True:
                async with lock:
                    if completed >= total_requests:
                        break
                    current = completed
                    completed += 1
                
                async with semaphore:
                    success, resp_time, status_code, error = await make_request(
                        session, url, method, request_data, timeout
                    )
                    result.add_result(success, resp_time, status_code, error)
                    
                    # 显示进度
                    async with lock:
                        current_completed = result.total_requests
                        if current_completed % max(1, total_requests // 20) == 0 or current_completed >= total_requests:
                            progress = min(100, (current_completed / total_requests) * 100)
                            bar_length = 20
                            filled = min(bar_length, int(bar_length * current_completed / total_requests))
                            bar = '█' * filled + '░' * (bar_length - filled)
                            print(f"\r进度: [{bar}] {current_completed}/{total_requests} ({progress:.1f}%)", end='', flush=True)
    
    # 创建并发任务
    tasks = [worker() for _ in range(concurrent)]
    await asyncio.gather(*tasks)
    
    print()  # 换行
    result.end_time = time.time()
    return result

def print_results(result: StressTestResult):
    """打印测试结果"""
    stats = result.get_stats()
    
    print_header("测试结果")
    
    print(f"{Colors.BOLD}基本统计:{Colors.RESET}")
    print(f"  - 总请求数: {stats['total_requests']}")
    print(f"  - 成功请求: {stats['successful_requests']} ({stats['success_rate']:.1f}%)")
    print(f"  - 失败请求: {stats['failed_requests']} ({stats['error_rate']:.1f}%)")
    print(f"  - 测试耗时: {stats['duration']:.2f}秒")
    
    if stats['successful_requests'] > 0:
        print(f"\n{Colors.BOLD}性能指标:{Colors.RESET}")
        print(f"  - 平均响应时间: {stats['avg_response_time']:.2f}ms")
        print(f"  - 中位数响应时间: {stats['median_response_time']:.2f}ms")
        print(f"  - P95响应时间: {stats['p95_response_time']:.2f}ms")
        print(f"  - P99响应时间: {stats['p99_response_time']:.2f}ms")
        print(f"  - 最小响应时间: {stats['min_response_time']:.2f}ms")
        print(f"  - 最大响应时间: {stats['max_response_time']:.2f}ms")
        print(f"  - 吞吐量: {stats['qps']:.2f} QPS")
        
        # 响应时间分布
        times = result.response_times
        if times:
            print(f"\n{Colors.BOLD}响应时间分布:{Colors.RESET}")
            ranges = [
                ("< 50ms", lambda x: x < 50),
                ("50-100ms", lambda x: 50 <= x < 100),
                ("100-200ms", lambda x: 100 <= x < 200),
                ("200-500ms", lambda x: 200 <= x < 500),
                ("> 500ms", lambda x: x >= 500)
            ]
            for label, condition in ranges:
                count = sum(1 for t in times if condition(t))
                percentage = (count / len(times) * 100) if times else 0
                print(f"  - {label}: {count} ({percentage:.1f}%)")
    
    if stats['status_codes']:
        print(f"\n{Colors.BOLD}状态码分布:{Colors.RESET}")
        for code, count in sorted(stats['status_codes'].items()):
            percentage = (count / stats['total_requests'] * 100) if stats['total_requests'] > 0 else 0
            print(f"  - {code}: {count} ({percentage:.1f}%)")
    
    if stats['errors']:
        print(f"\n{Colors.BOLD}错误统计:{Colors.RESET}")
        for error, count in stats['errors'].items():
            print(f"  - {error}: {count}")
    
    # 判断测试是否通过
    if stats['success_rate'] >= 95 and stats['avg_response_time'] < 1000:
        print_success("压力测试通过")
    elif stats['success_rate'] >= 90:
        print_warning("压力测试基本通过，但存在一些问题")
    else:
        print_error("压力测试失败")

def save_report(result: StressTestResult, output_file: str, config: Dict):
    """保存测试报告"""
    stats = result.get_stats()
    report = {
        "timestamp": datetime.now().isoformat(),
        "config": config,
        "results": stats
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print_info(f"测试报告已保存到: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Elder Company 压力测试')
    parser.add_argument('--base-url', default='http://localhost:8000', 
                       help='API基础URL (默认: http://localhost:8000)')
    parser.add_argument('--endpoint', default='/health', 
                       help='测试端点 (默认: /health)')
    parser.add_argument('--concurrent', type=int, default=10, 
                       help='并发用户数 (默认: 10)')
    parser.add_argument('--requests', type=int, default=100, 
                       help='总请求数 (默认: 100)')
    parser.add_argument('--method', default='GET', choices=['GET', 'POST'], 
                       help='HTTP方法 (默认: GET)')
    parser.add_argument('--timeout', type=int, default=30, 
                       help='请求超时时间（秒）(默认: 30)')
    parser.add_argument('--output', default=None, 
                       help='输出报告文件路径 (可选)')
    parser.add_argument('--data', default=None, 
                       help='POST请求的JSON数据 (JSON字符串)')
    
    args = parser.parse_args()
    
    print_header("Elder Company - 压力测试")
    
    print(f"{Colors.BOLD}测试配置:{Colors.RESET}")
    print(f"  - 端点: {args.endpoint}")
    print(f"  - 并发数: {args.concurrent}")
    print(f"  - 总请求数: {args.requests}")
    print(f"  - HTTP方法: {args.method}")
    print(f"  - 超时时间: {args.timeout}秒")
    print()
    
    # 解析POST数据
    request_data = None
    if args.method == 'POST' and args.data:
        try:
            request_data = json.loads(args.data)
        except json.JSONDecodeError:
            print_error(f"无效的JSON数据: {args.data}")
            return
    
    # 运行测试
    try:
        result = asyncio.run(run_stress_test(
            args.base_url, args.endpoint, args.concurrent, 
            args.requests, args.method, request_data, args.timeout
        ))
        
        # 打印结果
        print_results(result)
        
        # 保存报告
        if args.output:
            config = {
                "base_url": args.base_url,
                "endpoint": args.endpoint,
                "concurrent": args.concurrent,
                "total_requests": args.requests,
                "method": args.method,
                "timeout": args.timeout
            }
            save_report(result, args.output, config)
    
    except KeyboardInterrupt:
        print_warning("\n测试被用户中断")
    except Exception as e:
        print_error(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
