# shouldpy
> *"已有的测试该怎么写就怎么写，AI 再帮你加一道自然语言安检。"*

[![PyPI](https://img.shields.io/pypi/v/shouldpy.svg)](https://pypi.org/project/shouldpy/)
[![Python](https://img.shields.io/pypi/pyversions/shouldpy.svg)](https://pypi.org/project/shouldpy/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Build Status](https://github.com/zhixiangxue/should-ai/workflows/发布到%20PyPI/badge.svg)](https://github.com/zhixiangxue/should-ai/actions)
[![Downloads](https://img.shields.io/pypi/dm/shouldpy.svg)](https://pypi.org/project/shouldpy/)

## ❓ 这是什么？
仅200多行的小工具：给现有测试函数加一层 **@should("自然语言期望")** 装饰器
AI 会在函数跑完后 **检查** 所有日志、print 输出、返回值，  
判断“期望”是否达成 ——  **PASS** 安静通过；**FAIL: 原因** 抛 `AssertionError`。  

> 不替代 `assert`，不强制 `return`，不改造`testcase`；  
> 仅用一个装饰器让 **LLM 再帮你把把关**。

---

## ⚡️ 安装

```bash
pip install shouldpy

# 其他依赖，按需安装
pip install pytest-asyncio
pip install langchain-openai
```

---

## 👨🏻‍💻 例子

```python
from should import should
from langchain_openai import ChatOpenAI

should.use(ChatOpenAI()) # 指定你的llm

@should("日志里应该明确表示下单成功")
def test_create_order():
    ...  # 原来的测试代码，该怎么写怎么写
    logging.info("订单创建成功")
    assert resp.status_code == 200
```

跑 `pytest` →  
- 原有 `assert` 检查状态码  
- AI 额外检查日志/输出/返回值里有没有“订单创建成功”之类的输出  
两步都过才算通过。

---

## ⚠️ 注意

1. **需要自备** LangChain 兼容 LLM（OpenAI、DeepSeek、Ollama…）。  
2. **不保证确定性** → 适合**教学、脚本、探索式测试、兜底方案**，别拿它当核心断言。  
3. **每次都要调模型** → **慢 + 花钱 + 数据安全** → 别塞进高频 CI；本地跑、CR 前抽查更划算；土豪忽略；无所谓数据安全的忽略。

---

## 🤝 反馈
[https://github.com/zhixiangxue/should-ai](https://github.com/zhixiangxue/should-ai)  
issue、PR、star 欢迎！

---

## 📄 License
MIT © 2025 zx