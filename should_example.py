import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import uuid
from langchain_openai import ChatOpenAI

from should import should

qwen3 = ChatOpenAI(**{
    "api_key": "sk-1f97fc05349f4f7cb15e5e34de4805a7",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "model": "qwen-plus",
})

# 配置LLM客户端
should.use(qwen3)


# ============== 只使用print输出的业务函数 ==============

def register_user_with_print(name: str, age: int) -> str:
    """只使用print输出的注册函数，有bug：未成年人也能注册成功"""
    user_id = str(uuid.uuid4())

    # 使用print而不是logging
    print(f"开始注册用户: {name}, 年龄: {age}")

    if age < 18:
        print("警告: 检测到未成年人注册请求")
        # bug: 应该拒绝但没有拒绝
        print(f"注册成功! 用户ID: {user_id}")
    else:
        print(f"成年人注册验证通过")
        print(f"注册成功! 用户ID: {user_id}")

    return user_id


async def async_register_user_with_print(name: str, age: int) -> str:
    """异步版本，只使用print输出"""
    await asyncio.sleep(0.1)  # 模拟异步操作
    user_id = str(uuid.uuid4())

    print(f"异步注册开始: {name}, 年龄: {age}")

    if age < 18:
        print("异步检测: 未成年人注册请求")
        # bug: 应该拒绝但没有拒绝  
        print(f"异步注册完成! 用户ID: {user_id}")
    else:
        print(f"异步成年人验证通过")
        print(f"异步注册完成! 用户ID: {user_id}")

    return user_id


def calculate_discount(age: int, is_student: bool = False) -> float:
    """计算折扣的函数，只使用print输出"""
    print(f"计算折扣: 年龄={age}, 学生={is_student}")

    discount = 0.0

    if age < 18:
        discount = 0.2
        print(f"未成年人折扣: {discount}")
    elif is_student:
        discount = 0.1
        print(f"学生折扣: {discount}")
    else:
        print("无折扣")

    print(f"最终折扣: {discount}")
    return discount


# ============== 测试函数 ==============

@should("注册未成年人时必须拒绝并明确提示")
def test_print_register_minor():
    """测试只有print输出的未成年人注册"""
    result = register_user_with_print("小明", 16)
    return result


@should("成年人注册应该成功并有成功提示")
def test_print_register_adult():
    """测试只有print输出的成年人注册"""
    result = register_user_with_print("张三", 25)
    return result


@should("未成年人应该享受20%的折扣")
def test_minor_discount():
    """测试未成年人折扣计算"""
    discount = calculate_discount(16)
    return discount


@should("学生应该享受10%的折扣")
def test_student_discount():
    """测试学生折扣计算"""
    discount = calculate_discount(20, is_student=True)
    return discount


@should("异步注册未成年人时必须拒绝")
async def test_async_print_register_minor():
    """测试异步print输出的未成年人注册"""
    result = await async_register_user_with_print("小红", 15)
    return result


@should("异步成年人注册应该成功")
async def test_async_print_register_adult():
    """测试异步print输出的成年人注册"""
    result = await async_register_user_with_print("李四", 30)
    return result


# ============== 测试运行器 ==============

def run_print_tests():
    """运行print输出的同步测试"""
    print("🔄 开始测试只有print输出的同步函数...")

    tests = [
        ("test_print_register_minor", test_print_register_minor),
        ("test_print_register_adult", test_print_register_adult),
        ("test_minor_discount", test_minor_discount),
        ("test_student_discount", test_student_discount)
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"\n--- 运行 {test_name} ---")
        try:
            result = test_func()
            print(f"✅ {test_name} 通过")
            passed += 1
        except AssertionError as e:
            print(f"❌ {test_name} 失败: {e}")
            failed += 1
        except Exception as e:
            print(f"💥 {test_name} 出错: {e}")
            failed += 1

    print(f"\n📊 Print测试结果: {passed} 个通过, {failed} 个失败")
    return passed, failed


async def run_async_print_tests():
    """运行print输出的异步测试"""
    print("\n🔄 开始测试只有print输出的异步函数...")

    tests = [
        ("test_async_print_register_minor", test_async_print_register_minor),
        ("test_async_print_register_adult", test_async_print_register_adult)
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"\n--- 运行 {test_name} ---")
        try:
            result = await test_func()
            print(f"✅ {test_name} 通过")
            passed += 1
        except AssertionError as e:
            print(f"❌ {test_name} 失败: {e}")
            failed += 1
        except Exception as e:
            print(f"💥 {test_name} 出错: {e}")
            failed += 1

    print(f"\n📊 异步Print测试结果: {passed} 个通过, {failed} 个失败")
    return passed, failed


async def main():
    """主函数：演示print输出捕获"""
    print("🚀 AI 测试框架 - Print 输出捕获示例")
    print("=" * 60)

    # 运行print输出的同步测试
    sync_passed, sync_failed = run_print_tests()

    # 运行print输出的异步测试
    async_passed, async_failed = await run_async_print_tests()

    # 总结
    total_passed = sync_passed + async_passed
    total_failed = sync_failed + async_failed
    total_tests = total_passed + total_failed

    print("\n" + "=" * 60)
    print(f"🏁 Print输出测试总结:")
    print(f"   总测试数: {total_tests}")
    print(f"   通过: {total_passed}")
    print(f"   失败: {total_failed}")
    print(f"   成功率: {total_passed / total_tests * 100:.1f}%" if total_tests > 0 else "   成功率: 0%")

    if total_failed > 0:
        print(f"\n⚠️  AI通过分析print输出发现了 {total_failed} 个业务逻辑问题！")
    else:
        print(f"\n🎉 所有基于print输出的测试都通过了！")


if __name__ == "__main__":
    asyncio.run(main())
