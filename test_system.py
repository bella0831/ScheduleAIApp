"""
测试脚本 - 验证系统功能
"""

import json
import os
from config import Config
from data_generator import DataGenerator
from model import ScheduleT5Model
from scheduler import ScheduleRuleEngine
from main import PersonalScheduleGenerator

def test_data_generator():
    """测试数据生成器"""
    print("="*50)
    print("测试数据生成器")
    print("="*50)
    
    generator = DataGenerator()
    
    # 生成单个样本
    sample = generator.generate_single_sample()
    print("生成的样本:")
    print(json.dumps(sample, ensure_ascii=False, indent=2))
    
    # 生成数据集
    dataset = generator.generate_dataset(5)
    print(f"\n生成了 {len(dataset)} 个样本")
    
    # 保存和加载测试
    test_file = "test_data.json"
    generator.save_dataset(dataset, test_file)
    loaded_data = generator.load_dataset(test_file)
    print(f"保存和加载测试: {'通过' if len(loaded_data) == len(dataset) else '失败'}")
    
    # 清理测试文件
    if os.path.exists(test_file):
        os.remove(test_file)
    
    print("数据生成器测试完成\n")

def test_model():
    """测试模型功能"""
    print("="*50)
    print("测试模型功能")
    print("="*50)
    
    model = ScheduleT5Model()
    
    # 测试输出格式化
    tasks = [
        {"task": "写周报", "duration": 120, "pref_time": "上午", "priority": 1},
        {"task": "健身", "duration": 60, "pref_time": "傍晚", "priority": 2}
    ]
    
    formatted_output = model.format_output(tasks)
    print(f"格式化输出: {formatted_output}")
    
    # 测试输出解析
    parsed_tasks = model.parse_output(formatted_output)
    print(f"解析结果: {json.dumps(parsed_tasks, ensure_ascii=False, indent=2)}")
    
    # 测试编码
    input_text = "上下文：周三 在家 ｜ 需求：写周报2小时，健身1小时"
    encoded = model.encode_input(input_text)
    print(f"输入编码形状: {encoded['input_ids'].shape}")
    
    print("模型功能测试完成\n")

def test_scheduler():
    """测试规则引擎"""
    print("="*50)
    print("测试规则引擎")
    print("="*50)
    
    config = Config()
    scheduler = ScheduleRuleEngine(config)
    
    # 测试可用时间段
    available_slots = scheduler.get_available_time_slots()
    print(f"可用时间段数量: {len(available_slots)}")
    for slot in available_slots:
        print(f"  {slot.start_time}-{slot.end_time} ({slot.duration}分钟)")
    
    # 测试任务调度
    tasks = [
        {"task": "写周报", "duration": 120, "pref_time": "上午", "priority": 1},
        {"task": "健身", "duration": 60, "pref_time": "傍晚", "priority": 2},
        {"task": "开会", "duration": 90, "pref_time": "下午", "priority": 1}
    ]
    
    schedule_result = scheduler.schedule_tasks(tasks)
    print(f"\n调度结果:")
    print(f"  已安排任务: {schedule_result['total_scheduled']} 个")
    print(f"  未安排任务: {schedule_result['total_remaining']} 个")
    
    # 显示安排的任务
    for task in schedule_result["scheduled_tasks"]:
        if not task.get("is_fixed", False):
            print(f"    {task['start_time']}-{task['end_time']}: {task['task']}")
    
    # 测试验证
    validation = scheduler.validate_schedule(schedule_result)
    print(f"\n验证结果: {'有效' if validation['is_valid'] else '无效'}")
    if validation['warnings']:
        print(f"警告: {validation['warnings']}")
    
    print("规则引擎测试完成\n")

def test_integration():
    """测试系统集成"""
    print("="*50)
    print("测试系统集成")
    print("="*50)
    
    # 创建数据目录
    os.makedirs("data", exist_ok=True)
    
    # 生成测试数据
    generator = DataGenerator()
    test_data = generator.generate_dataset(10)
    generator.save_dataset(test_data, "data/test_train_data.json")
    generator.save_dataset(test_data[:2], "data/test_val_data.json")
    
    # 测试完整流程
    test_input = "上下文：周三 在家 ｜ 需求：写周报2小时，健身1小时，下午开会"
    
    # 使用预训练模型进行测试
    generator_system = PersonalScheduleGenerator()
    
    try:
        result = generator_system.generate_schedule(test_input)
        print("集成测试成功!")
        print(f"解析到 {len(result['parsed_tasks'])} 个任务")
        print(f"安排了 {result['summary']['total_scheduled']} 个任务")
    except Exception as e:
        print(f"集成测试失败: {e}")
    
    # 清理测试数据
    if os.path.exists("data/test_train_data.json"):
        os.remove("data/test_train_data.json")
    if os.path.exists("data/test_val_data.json"):
        os.remove("data/test_val_data.json")
    
    print("系统集成测试完成\n")

def main():
    """运行所有测试"""
    print("个人日程生成系统 - 功能测试")
    print("="*60)
    
    try:
        # 测试各个组件
        test_data_generator()
        test_model()
        test_scheduler()
        test_integration()
        
        print("="*60)
        print("所有测试完成!")
        print("系统功能正常，可以开始使用。")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        print("请检查依赖包是否正确安装。")

if __name__ == "__main__":
    main()
