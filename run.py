"""
快速启动脚本 - 个人日程生成系统
"""

from main import PersonalScheduleGenerator

def quick_demo():
    """快速演示"""
    print("个人日程生成系统 - 快速演示")
    print("="*50)
    
    # 初始化系统
    generator = PersonalScheduleGenerator()
    
    # 演示用例
    demo_inputs = [
        "上下文：周三 在家 ｜ 需求：写周报2小时，健身1小时，下午开会",
        "上下文：周五 公司 ｜ 需求：学习编程3小时，阅读1小时，团队会议",
        "上下文：周六 在家 ｜ 需求：打扫卫生1小时，看电影2小时，散步30分钟，冥想20分钟"
    ]
    
    for i, input_text in enumerate(demo_inputs, 1):
        print(f"\n演示 {i}:")
        print("-" * 30)
        
        # 生成日程
        result = generator.generate_schedule(input_text)
        
        # 打印结果
        generator.print_schedule(result)
        
        print("\n" + "="*50)

def interactive_demo():
    """交互式演示"""
    print("个人日程生成系统 - 交互式演示")
    print("="*50)
    print("输入您的日程需求，系统将自动生成日程安排")
    print("输入 'quit' 退出，输入 'example' 查看示例")
    print()
    
    generator = PersonalScheduleGenerator()
    
    while True:
        try:
            user_input = input("请输入日程需求: ").strip()
            
            if user_input.lower() == 'quit':
                print("再见!")
                break
            
            if user_input.lower() == 'example':
                examples = generator.generate_example_data(3)
                print("\n示例输入:")
                for i, example in enumerate(examples, 1):
                    print(f"{i}. {example['input_text']}")
                continue
            
            if not user_input:
                print("请输入有效的日程需求")
                continue
            
            # 生成日程
            result = generator.generate_schedule(user_input)
            
            # 打印结果
            generator.print_schedule(result)
            
        except KeyboardInterrupt:
            print("\n\n再见!")
            break
        except Exception as e:
            print(f"发生错误: {e}")

def main():
    """主函数"""
    print("选择运行模式:")
    print("1. 快速演示 (自动运行预设示例)")
    print("2. 交互式演示 (手动输入)")
    
    while True:
        choice = input("\n请选择 (1/2): ").strip()
        
        if choice == "1":
            quick_demo()
            break
        elif choice == "2":
            interactive_demo()
            break
        else:
            print("请输入 1 或 2")

if __name__ == "__main__":
    main()
