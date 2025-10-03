#!/usr/bin/env python3
"""
测试 AgentLLM 类的功能
"""
# %%
from PIL import Image
import io
import base64

# 测试导入
try:
    import sys
    import os
    # 添加父目录到路径，以便导入包
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)
    
    from lmitf import AgentLLM
    print("✓ 成功导入 AgentLLM")
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    exit(1)

def create_test_image():
    """创建一个简单的测试图片"""
    from PIL import Image, ImageDraw
    
    # 创建一个简单的测试图片
    img = Image.new('RGB', (100, 100), color='red')
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, 90, 90], fill='blue')
    draw.text((30, 40), "TEST", fill='white')
    
    return img

def test_basic_functionality():
    """测试基本功能"""
    print("\n=== 测试基本功能 ===")
    
    try:
        # 初始化客户端
        agent = AgentLLM()
        print("✓ 成功初始化 AgentLLM")
        
        # 测试消息构建功能
        test_image = create_test_image()
        messages = agent._build_vision_messages("这是什么颜色？", test_image)
        
        print("✓ 成功构建视觉消息")
        print(f"  消息结构: {type(messages)} 包含 {len(messages)} 条消息")
        print(f"  内容类型: {[item['type'] for item in messages[0]['content']]}")
        
    except Exception as e:
        print(f"✗ 基本功能测试失败: {e}")
        return False
    
    return True

def test_message_building():
    """测试消息构建功能"""
    print("\n=== 测试消息构建 ===")
    
    agent = AgentLLM()
    test_image = create_test_image()
    
    # 测试只有文本
    try:
        messages = agent._build_vision_messages("纯文本测试", None)
        assert len(messages[0]['content']) == 1
        assert messages[0]['content'][0]['type'] == 'text'
        print("✓ 纯文本消息构建成功")
    except Exception as e:
        print(f"✗ 纯文本消息构建失败: {e}")
        return False
    
    # 测试只有图片
    try:
        messages = agent._build_vision_messages(None, test_image)
        assert len(messages[0]['content']) == 1
        assert messages[0]['content'][0]['type'] == 'image_url'
        print("✓ 纯图片消息构建成功")
    except Exception as e:
        print(f"✗ 纯图片消息构建失败: {e}")
        return False
    
    # 测试文本+图片
    try:
        messages = agent._build_vision_messages("描述这张图片", test_image)
        assert len(messages[0]['content']) == 2
        assert messages[0]['content'][0]['type'] == 'text'
        assert messages[0]['content'][1]['type'] == 'image_url'
        print("✓ 文本+图片消息构建成功")
    except Exception as e:
        print(f"✗ 文本+图片消息构建失败: {e}")
        return False
    
    # 测试多图片
    try:
        images = [test_image, test_image]
        messages = agent._build_vision_messages("比较这些图片", images)
        assert len(messages[0]['content']) == 3  # 1个文本 + 2个图片
        print("✓ 多图片消息构建成功")
    except Exception as e:
        print(f"✗ 多图片消息构建失败: {e}")
        return False
    
    return True

def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===")
    
    agent = AgentLLM()
    
    # 测试空输入
    try:
        agent._build_vision_messages(None, None)
        print("✗ 应该抛出 ValueError")
        return False
    except ValueError:
        print("✓ 正确处理空输入错误")
    except Exception as e:
        print(f"✗ 意外错误: {e}")
        return False
    
    # 测试图片数量限制
    try:
        test_image = create_test_image()
        too_many_images = [test_image] * 11  # 超过10张
        agent._build_vision_messages("测试", too_many_images)
        print("✗ 应该抛出图片数量限制错误")
        return False
    except ValueError as e:
        if "Maximum 10 images" in str(e):
            print("✓ 正确处理图片数量限制")
        else:
            print(f"✗ 错误类型不正确: {e}")
            return False
    except Exception as e:
        print(f"✗ 意外错误: {e}")
        return False
    
    return True

def main():
    """主测试函数"""
    print("AgentLLM 功能测试")
    print("=" * 40)
    
    all_tests_passed = True
    
    # 运行测试
    all_tests_passed &= test_basic_functionality()
    all_tests_passed &= test_message_building()
    all_tests_passed &= test_error_handling()
    
    print("\n" + "=" * 40)
    if all_tests_passed:
        print("🎉 所有测试通过!")
    else:
        print("❌ 部分测试失败")
    
    print("\n注意: 这些测试只验证了代码结构和消息构建功能。")
    print("实际的 API 调用需要有效的 OpenAI API 密钥和网络连接。")

if __name__ == "__main__":
    main()
#%%
from lmitf import AgentLLM
agent = AgentLLM()
img = Image.new('RGB', (100, 100), color = 'red')
messages = agent._build_vision_messages("这是什么颜色？", img)
res = agent.call_with_vision(
    text="这是什么颜色？",
    images=img,
    response_format='text'
)
# %%