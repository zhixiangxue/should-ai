import functools
import inspect
import io
import json
import logging
import sys
import textwrap

from langchain_core.language_models import BaseChatModel


class ShouldDecorator:
    """
    AI-driven test assertion decorator class

    Usage:
    from shouldpy import should

    should.use(llm)  # Configure LLM

    @should("Expected condition")
    def test_function():
        return some_result()
    """

    def __init__(self):
        self._llm_client = None

    def use(self, llm_client: BaseChatModel):
        """
        Configure LLM client

        Args:
            llm_client: LLM client object with invoke method

        Returns:
            self: Support method chaining
        """
        self._llm_client = llm_client
        return self

    def __call__(self, condition: str, llm_client=None):
        """
        Decorator call method

        Args:
            condition: Natural language description of expected condition
            llm_client: Optional LLM client, uses global configuration if not provided

        Returns:
            Decorator function
        """

        def decorator(test_func):
            # Determine which LLM client to use
            effective_llm = llm_client if llm_client is not None else self._llm_client
            if effective_llm is None:
                raise ValueError(
                    "No LLM client configured, please use should.use(llm) to configure or pass llm_client parameter in decorator"
                )
            if inspect.iscoroutinefunction(test_func):
                # Handle async functions
                @functools.wraps(test_func)
                async def async_wrapper(*args, **kwargs):
                    # Log and output capture containers
                    captured_logs = []
                    captured_prints = []

                    # Create standard logging handler
                    class LogCapture(logging.Handler):
                        def emit(self, record):
                            captured_logs.append(
                                {
                                    "message": self.format(record),
                                    "level": record.levelname,
                                    "timestamp": record.created,
                                }
                            )

                    # Create print output capturer
                    class PrintCapture(io.StringIO):
                        def write(self, s):
                            if s.strip():  # Ignore empty lines
                                captured_prints.append(s.strip())
                            return super().write(s)

                    # Add log capturer
                    log_capture = LogCapture()
                    root_logger = logging.getLogger()
                    root_logger.addHandler(log_capture)
                    original_level = root_logger.level
                    root_logger.setLevel(logging.INFO)

                    # Capture print output
                    original_stdout = sys.stdout
                    print_capture = PrintCapture()
                    sys.stdout = print_capture

                    try:
                        # Execute the decorated async function
                        actual_result = await test_func(*args, **kwargs)

                        # Call AI for judgment
                        verdict = _call_ai_model(
                            condition, captured_logs, captured_prints, actual_result, effective_llm
                        )
                        if not verdict.startswith("PASS"):
                            raise AssertionError(f"AI assertion failed: {verdict}")

                        return actual_result

                    finally:
                        # Restore standard output
                        sys.stdout = original_stdout
                        # Clean up log handler
                        root_logger.removeHandler(log_capture)
                        root_logger.setLevel(original_level)

                return async_wrapper

            else:
                # Handle sync functions
                @functools.wraps(test_func)
                def sync_wrapper(*args, **kwargs):
                    # Log and output capture containers
                    captured_logs = []
                    captured_prints = []

                    # Create standard logging handler
                    class LogCapture(logging.Handler):
                        def emit(self, record):
                            captured_logs.append(
                                {
                                    "message": self.format(record),
                                    "level": record.levelname,
                                    "timestamp": record.created,
                                }
                            )

                    # Create print output capturer
                    class PrintCapture(io.StringIO):
                        def write(self, s):
                            if s.strip():  # Ignore empty lines
                                captured_prints.append(s.strip())
                            return super().write(s)

                    # Add log capturer
                    log_capture = LogCapture()
                    root_logger = logging.getLogger()
                    root_logger.addHandler(log_capture)
                    original_level = root_logger.level
                    root_logger.setLevel(logging.INFO)

                    # Capture print output
                    original_stdout = sys.stdout
                    print_capture = PrintCapture()
                    sys.stdout = print_capture

                    try:
                        # Execute the decorated sync function
                        actual_result = test_func(*args, **kwargs)

                        # Call AI for judgment
                        verdict = _call_ai_model(
                            condition, captured_logs, captured_prints, actual_result, effective_llm
                        )
                        if not verdict.startswith("PASS"):
                            raise AssertionError(verdict)

                        return actual_result

                    finally:
                        # Restore standard output
                        sys.stdout = original_stdout
                        # Clean up log handler
                        root_logger.removeHandler(log_capture)
                        root_logger.setLevel(original_level)

                return sync_wrapper

        return decorator


def _call_ai_model(
    condition: str, logs: list[dict], prints: list[str], actual_result=None, llm_client=None
) -> str:
    """
    Call AI model for judgment

    Args:
        condition: Natural language description of expected condition
        logs: List of captured logs
        prints: List of captured print outputs
        actual_result: Actual return result of the function
        llm_client: LLM client object

    Returns:
        AI judgment result, starting with "PASS" or "FAIL:"
    """
    if llm_client is None:
        return "FAIL: No LLM client configured"

    # Build prompt
    prompt = textwrap.dedent(
        f"""
    Below is the context information from a test execution, expected condition: "{condition}"
    
    Execution logs:
    {json.dumps(logs, ensure_ascii=False, indent=2) if logs else "No log output"}
    
    Print outputs:
    {json.dumps(prints, ensure_ascii=False, indent=2) if prints else "No print output"}
    
    Function return result:
    {actual_result}
    
    Please judge whether the expected condition is satisfied based on logs, print outputs and return result. Response format:
    PASS  or  FAIL: specific reason
    No additional explanation needed.
    """
    )

    try:
        response = llm_client.invoke(prompt)
        # 确保返回的是字符串类型
        content = response.content
        if isinstance(content, str):
            return content
        else:
            return str(content) if content is not None else "FAIL: Empty response from AI"
    except Exception as e:
        return f"FAIL: AI call failed - {str(e)}"


# Create global instance
should = ShouldDecorator()
