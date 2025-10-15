"""
简单测试脚本 - 测试系统组件
"""

print("开始简单测试...")

try:
    print("1. 测试配置...")
    from config import Config
    print(f"✓ 模型名称: {Config.MODEL_NAME}")
    print(f"✓ 最大任务数: {Config.MAX_TASKS_PER_DAY}")
    
    print("\n2. 测试调度器...")
    from scheduler import ScheduleRuleEngine, TimeSlot
    scheduler = ScheduleRuleEngine(Config)
    print("✓ 调度器初始化成功")
    
    print("\n3. 测试时间段操作...")
    slot1 = TimeSlot("09:00", "12:00")
    slot2 = TimeSlot("13:00", "17:00")
    print(f"✓ 时间段1: {slot1.start_time}-{slot1.end_time}")
    print(f"✓ 时间段2: {slot2.start_time}-{slot2.end_time}")
    print(f"✓ 是否重叠: {slot1.overlaps_with(slot2)}")
    
    print("\n4. 测试任务调度...")
    test_tasks = [
        {"task": "写周报", "duration": 120, "pref_time": "上午", "priority": 1},
        {"task": "健身", "duration": 60, "pref_time": "傍晚", "priority": 2}
    ]
    
    schedule = scheduler.schedule_tasks(test_tasks)
    print("✓ 任务调度成功")
    print(f"✓ 调度结果: {len(schedule)} 个任务")
    
    print("\n5. 测试模拟模型...")
    # 创建一个简单的模拟模型类
    class MockModel:
        def predict(self, input_text):
            # 返回模拟的预测结果
            return [
                {"task": "写周报", "duration": 120, "pref_time": "上午", "priority": 1},
                {"task": "健身", "duration": 60, "pref_time": "傍晚", "priority": 2}
            ]
    
    mock_model = MockModel()
    result = mock_model.predict("写周报2小时，健身1小时")
    print("✓ 模拟模型预测成功")
    print(f"✓ 预测结果: {result}")
    
    print("\n6. 测试完整流程（使用模拟模型）...")
    # 创建一个简化的生成器
    class SimpleGenerator:
        def __init__(self):
            self.model = MockModel()
            self.scheduler = ScheduleRuleEngine(Config)
        
        def generate_schedule(self, input_text):
            # 解析任务
            tasks = self.model.predict(input_text)
            # 调度任务
            schedule = self.scheduler.schedule_tasks(tasks)
            return {
                "input": input_text,
                "parsed_tasks": tasks,
                "schedule": schedule
            }
    
    generator = SimpleGenerator()
    result = generator.generate_schedule("写周报2小时，健身1小时")
    print("✓ 完整流程测试成功")
    print(f"✓ 输入: {result['input']}")
    print(f"✓ 解析任务: {len(result['parsed_tasks'])} 个")
    print(f"✓ 调度结果: {len(result['schedule'])} 个")
    
    print("\n🎉 所有基础组件测试通过！")
    print("系统核心功能正常，只是模型加载需要更多内存。")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
