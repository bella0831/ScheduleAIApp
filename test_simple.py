#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试脚本 - 验证Python和依赖包安装
"""

def test_python():
    """测试Python基本功能"""
    print("="*50)
    print("Python 安装验证")
    print("="*50)
    
    import sys
    print(f"Python 版本: {sys.version}")
    print(f"Python 路径: {sys.executable}")
    print("✓ Python 安装成功!")
    print()

def test_dependencies():
    """测试依赖包安装"""
    print("="*50)
    print("依赖包安装验证")
    print("="*50)
    
    dependencies = [
        ("torch", "PyTorch"),
        ("transformers", "Transformers"),
        ("numpy", "NumPy"),
        ("pandas", "Pandas"),
        ("scikit-learn", "Scikit-learn"),
        ("matplotlib", "Matplotlib"),
        ("tqdm", "TQDM")
    ]
    
    all_installed = True
    
    for package, name in dependencies:
        try:
            __import__(package)
            print(f"✓ {name} 安装成功")
        except ImportError:
            print(f"✗ {name} 安装失败")
            all_installed = False
    
    print()
    if all_installed:
        print("✓ 所有依赖包安装成功!")
    else:
        print("✗ 部分依赖包安装失败，请运行: pip install -r requirements.txt")
    
    return all_installed

def test_basic_functionality():
    """测试基本功能"""
    print("="*50)
    print("基本功能测试")
    print("="*50)
    
    try:
        # 测试基本计算
        import numpy as np
        result = np.array([1, 2, 3]) + np.array([4, 5, 6])
        print("✓ NumPy 基本计算正常")
        
        # 测试PyTorch
        import torch
        tensor = torch.tensor([1, 2, 3])
        print("✓ PyTorch 张量操作正常")
        
        # 测试Transformers
        from transformers import T5Tokenizer
        tokenizer = T5Tokenizer.from_pretrained("t5-base")
        print("✓ Transformers 模型加载正常")
        
        print("✓ 基本功能测试通过!")
        return True
        
    except Exception as e:
        print(f"✗ 基本功能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("个人日程生成系统 - 安装验证")
    print("="*60)
    
    # 测试Python
    test_python()
    
    # 测试依赖包
    deps_ok = test_dependencies()
    
    # 测试基本功能
    if deps_ok:
        func_ok = test_basic_functionality()
    else:
        func_ok = False
    
    # 总结
    print("="*60)
    print("测试总结")
    print("="*60)
    
    if deps_ok and func_ok:
        print("🎉 恭喜! 系统安装成功，可以开始使用了!")
        print("\n下一步:")
        print("1. 运行 'python run.py' 开始使用")
        print("2. 查看 USAGE.md 了解详细使用方法")
        print("3. 查看 README.md 了解系统特性")
    else:
        print("❌ 安装存在问题，请检查:")
        print("1. Python 是否正确安装")
        print("2. 依赖包是否完整安装")
        print("3. 网络连接是否正常")
        print("\n请参考 INSTALL.md 进行故障排除")

if __name__ == "__main__":
    main()
