import json
import functools
import inspect
import textwrap
import logging
import sys
import io

from langchain_core.language_models import BaseChatModel


class ShouldDecorator:
    """
    AI驱动的测试断言装饰器类
    
    使用方式：
    from should import should
    
    should.use(llm)  # 配置LLM
    
    @should("期望条件")
    def test_function():
        return some_result()
    """

    def __init__(self):
        self._llm_client = None

    def use(self, llm_client: BaseChatModel):
        """
        配置LLM客户端
        
        Args:
            llm_client: 具有invoke方法的LLM客户端对象
        
        Returns:
            self: 支持链式调用
        """
        self._llm_client = llm_client
        return self

    def __call__(self, condition: str, llm_client=None):
        """
        装饰器调用方法
        
        Args:
            condition: 期望条件的自然语言描述
            llm_client: 可选的LLM客户端，如果不提供则使用全局配置
        
        Returns:
            装饰器函数
        """

        def decorator(test_func):
            # 确定使用哪个LLM客户端
            effective_llm = llm_client if llm_client is not None else self._llm_client
            if effective_llm is None:
                raise ValueError("没有配置LLM客户端，请使用should.use(llm)进行配置或在装饰器中传入llm_client参数")
            if inspect.iscoroutinefunction(test_func):
                # 处理异步函数
                @functools.wraps(test_func)
                async def async_wrapper(*args, **kwargs):
                    # 日志和输出捕获容器
                    captured_logs = []
                    captured_prints = []

                    # 创建标准logging处理器
                    class LogCapture(logging.Handler):
                        def emit(self, record):
                            captured_logs.append({
                                "message": self.format(record),
                                "level": record.levelname,
                                "timestamp": record.created
                            })

                    # 创建print输出捕获器
                    class PrintCapture(io.StringIO):
                        def write(self, s):
                            if s.strip():  # 忽略空行
                                captured_prints.append(s.strip())
                            return super().write(s)

                    # 添加日志捕获器
                    log_capture = LogCapture()
                    root_logger = logging.getLogger()
                    root_logger.addHandler(log_capture)
                    original_level = root_logger.level
                    root_logger.setLevel(logging.INFO)

                    # 捕获print输出
                    original_stdout = sys.stdout
                    print_capture = PrintCapture()
                    sys.stdout = print_capture

                    try:
                        # 执行被装饰的异步函数
                        actual_result = await test_func(*args, **kwargs)

                        # 调用AI判断
                        verdict = _call_ai_model(condition, captured_logs, captured_prints, actual_result,
                                                 effective_llm)
                        if not verdict.startswith("PASS"):
                            raise AssertionError(f"AI 断言失败: {verdict}")

                        return actual_result

                    finally:
                        # 恢复标准输出
                        sys.stdout = original_stdout
                        # 清理日志处理器
                        root_logger.removeHandler(log_capture)
                        root_logger.setLevel(original_level)

                return async_wrapper

            else:
                # 处理同步函数
                @functools.wraps(test_func)
                def sync_wrapper(*args, **kwargs):
                    # 日志和输出捕获容器
                    captured_logs = []
                    captured_prints = []

                    # 创建标准logging处理器
                    class LogCapture(logging.Handler):
                        def emit(self, record):
                            captured_logs.append({
                                "message": self.format(record),
                                "level": record.levelname,
                                "timestamp": record.created
                            })

                    # 创建print输出捕获器
                    class PrintCapture(io.StringIO):
                        def write(self, s):
                            if s.strip():  # 忽略空行
                                captured_prints.append(s.strip())
                            return super().write(s)

                    # 添加日志捕获器
                    log_capture = LogCapture()
                    root_logger = logging.getLogger()
                    root_logger.addHandler(log_capture)
                    original_level = root_logger.level
                    root_logger.setLevel(logging.INFO)

                    # 捕获print输出
                    original_stdout = sys.stdout
                    print_capture = PrintCapture()
                    sys.stdout = print_capture

                    try:
                        # 执行被装饰的同步函数
                        actual_result = test_func(*args, **kwargs)

                        # 调用AI判断
                        verdict = _call_ai_model(condition, captured_logs, captured_prints, actual_result,
                                                 effective_llm)
                        if not verdict.startswith("PASS"):
                            raise AssertionError(f"AI 断言失败: {verdict}")

                        return actual_result

                    finally:
                        # 恢复标准输出
                        sys.stdout = original_stdout
                        # 清理日志处理器
                        root_logger.removeHandler(log_capture)
                        root_logger.setLevel(original_level)

                return sync_wrapper

        return decorator


def _call_ai_model(condition: str, logs: list[dict], prints: list[str], actual_result=None, llm_client=None) -> str:
    """
    调用AI模型进行判断
    
    Args:
        condition: 期望条件的自然语言描述
        logs: 捕获的日志列表
        prints: 捕获的print输出列表
        actual_result: 函数的实际返回结果
        llm_client: LLM客户端对象
    
    Returns:
        AI的判断结果，以"PASS"或"FAIL:"开头
    """
    if llm_client is None:
        return "FAIL: 没有配置LLM客户端"

    # 构建提示词
    prompt = textwrap.dedent(f"""
    下面是一份测试执行的上下文信息，期望条件是："{condition}"
    
    执行日志:
    {json.dumps(logs, ensure_ascii=False, indent=2) if logs else "无日志输出"}
    
    Print输出:
    {json.dumps(prints, ensure_ascii=False, indent=2) if prints else "无print输出"}
    
    函数返回结果:
    {actual_result}
    
    请根据日志、print输出和返回结果判断是否满足期望条件，回复格式：
    PASS  或  FAIL: 具体原因
    无需多余解释。
    """)

    try:
        response = llm_client.invoke(prompt)
        print(">>>>>>>>>>>>>>>>>>>>>>>>", response.content)
        return response.content
    except Exception as e:
        return f"FAIL: AI调用失败 - {str(e)}"


# 创建全局实例
should = ShouldDecorator()
