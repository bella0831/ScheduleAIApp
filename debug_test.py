"""
调试测试脚本
"""

print("开始调试测试...")

try:
    print("1. 导入配置...")
    from config import Config
    print("✓ 配置导入成功")
    
    print("2. 导入模型...")
    from model import ScheduleT5Model
    print("✓ 模型类导入成功")
    
    print("3. 初始化模型...")
    model = ScheduleT5Model(Config.MODEL_NAME)
    print("✓ 模型初始化成功")
    
    print("4. 测试简单预测...")
    test_input = "写周报2小时"
    result = model.predict(test_input)
    print(f"✓ 预测结果: {result}")
    
    print("5. 导入调度器...")
    from scheduler import ScheduleRuleEngine
    print("✓ 调度器导入成功")
    
    print("6. 初始化调度器...")
    scheduler = ScheduleRuleEngine()
    print("✓ 调度器初始化成功")
    
    print("7. 测试完整流程...")
    from main import PersonalScheduleGenerator
    generator = PersonalScheduleGenerator()
    print("✓ 生成器初始化成功")
    
    print("8. 测试日程生成...")
    result = generator.generate_schedule("写周报2小时，健身1小时")
    print("✓ 日程生成成功")
    print(f"结果: {result}")
    
    print("\n🎉 所有测试通过！系统运行正常。")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
