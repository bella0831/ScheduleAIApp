# 安装指南

## 系统要求

- Windows 10/11
- Python 3.8 或更高版本
- 至少 4GB RAM
- 至少 2GB 可用磁盘空间

## 安装步骤

### 1. 安装 Python

#### 方法一：从官网下载
1. 访问 [Python官网](https://www.python.org/downloads/)
2. 下载最新版本的 Python 3.8+
3. 运行安装程序
4. **重要**: 勾选 "Add Python to PATH"
5. 选择 "Install Now"

#### 方法二：使用 Microsoft Store
1. 打开 Microsoft Store
2. 搜索 "Python"
3. 安装 Python 3.8 或更高版本

#### 验证安装
打开命令提示符或PowerShell，运行：
```bash
python --version
```
或
```bash
py --version
```

### 2. 安装依赖包

#### 创建虚拟环境（推荐）
```bash
# 创建虚拟环境
python -m venv schedule_env

# 激活虚拟环境
# Windows:
schedule_env\Scripts\activate

# 或使用 PowerShell:
schedule_env\Scripts\Activate.ps1
```

#### 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 验证安装

运行测试脚本：
```bash
python test_system.py
```

## 常见问题

### Python 未找到
如果 `python` 命令不可用：
1. 检查是否已安装 Python
2. 确保 Python 已添加到 PATH
3. 尝试使用 `py` 命令

### 依赖安装失败
如果某些包安装失败：
1. 更新 pip: `python -m pip install --upgrade pip`
2. 安装 Visual C++ 构建工具（如果需要）
3. 尝试使用预编译的轮子

### 内存不足
如果遇到内存错误：
1. 关闭其他程序
2. 减少批次大小
3. 使用CPU模式

## 快速验证

创建一个简单的测试文件 `test_simple.py`：

```python
print("Python 安装成功!")
print("开始测试系统组件...")

try:
    import torch
    print("✓ PyTorch 安装成功")
except ImportError:
    print("✗ PyTorch 安装失败")

try:
    import transformers
    print("✓ Transformers 安装成功")
except ImportError:
    print("✗ Transformers 安装失败")

try:
    import numpy
    print("✓ NumPy 安装成功")
except ImportError:
    print("✗ NumPy 安装失败")

print("测试完成!")
```

运行测试：
```bash
python test_simple.py
```

## 开发环境设置

### 推荐 IDE
- **VS Code**: 免费，功能强大
- **PyCharm**: 专业Python IDE
- **Jupyter Notebook**: 交互式开发

### VS Code 设置
1. 安装 Python 扩展
2. 选择 Python 解释器
3. 安装推荐的扩展包

## 故障排除

### 权限问题
如果遇到权限错误：
1. 以管理员身份运行命令提示符
2. 使用 `--user` 标志安装包
3. 检查防火墙设置

### 网络问题
如果下载包时遇到网络问题：
1. 使用国内镜像源
2. 配置代理设置
3. 尝试离线安装

### 版本兼容性
确保使用兼容的版本：
- Python 3.8-3.11
- PyTorch 1.9+
- Transformers 4.21+

## 下一步

安装完成后，请查看：
- [使用指南](USAGE.md)
- [README.md](README.md)

开始使用个人日程生成系统！
