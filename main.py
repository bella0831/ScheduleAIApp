"""
主程序 - 个人日程生成系统
"""

import json
print("Imported json")
import os
print("Imported os")
from typing import List, Dict, Any
print("Imported typing")
from config import Config
print("Imported config")
from model import ScheduleT5Model
print("Imported model")
from scheduler import ScheduleRuleEngine
print("Imported scheduler")
from data_generator import DataGenerator
print("Imported data_generator")
from lightweight_main import RuleBasedParser

print("Imported modules")

class PersonalScheduleGenerator:
    """个人日程生成系统"""
    
    def __init__(self, model_path: str = None):
        self.config = Config()
        
        # 初始化模型
        if model_path and os.path.exists(model_path):
            print(f"加载已训练的模型: {model_path}")
            self.model = ScheduleT5Model()
            self.model.load_model(model_path)
        else:
            print("使用预训练模型")
            self.model = ScheduleT5Model(self.config.MODEL_NAME)
        
        # 初始化规则引擎
        self.rule_engine = ScheduleRuleEngine(self.config)
        
        # 初始化数据生成器（用于生成示例数据）
        self.data_generator = DataGenerator()
        # 基于规则的解析器（回退方案）
        self.fallback_parser = RuleBasedParser()
    
    def generate_schedule(self, input_text: str) -> Dict[str, Any]:
        """生成个人日程。

        流程：
        1) 先用 T5 模型解析任务；若解析为空，使用规则解析回退，保证后续有可调度的任务。
        2) 使用规则引擎进行调度，产出包含已安排与未安排任务的 schedule 结构。
        3) 验证日程，输出 is_valid 与错误/警告信息。
        4) 汇总统计信息，统一返回结构化结果。
        """
        print(f"输入: {input_text}")
        
        # 1. 使用模型解析任务
        print("\n1. 解析任务...")
        tasks = self.model.predict_tasks(input_text)
        # 如果模型未能解析出任务，则使用规则解析作为回退，确保后续始终有 schedule 结构
        if not tasks:
            print("模型未能解析任务，使用规则解析回退...")
            tasks = self.fallback_parser.parse_tasks(input_text)
        
        print("解析的任务:")
        for task in tasks:
            print(f"  - {task['task']}: {task['duration']}分钟, {task['pref_time']}, 优先级{task['priority']}")
        
        # 2. 使用规则引擎安排日程
        print("\n2. 安排日程...")
        schedule_result = self.rule_engine.schedule_tasks(tasks)
        
        # 3. 验证日程
        print("\n3. 验证日程...")
        validation_result = self.rule_engine.validate_schedule(schedule_result)
        
        # 4. 格式化输出
        result = {
            "input": input_text,
            "parsed_tasks": tasks,
            "schedule": schedule_result,
            "validation": validation_result,
            "summary": self._generate_summary(schedule_result, validation_result)
        }
        
        return result
    
    def _generate_summary(self, schedule_result: Dict[str, Any], validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成日程摘要"""
        scheduled_tasks = schedule_result["scheduled_tasks"]
        remaining_tasks = schedule_result["remaining_tasks"]
        
        # 计算总时长
        total_duration = sum(task["duration"] for task in scheduled_tasks if not task.get("is_fixed", False))
        
        # 统计各时间段任务
        time_distribution = {}
        for task in scheduled_tasks:
            if not task.get("is_fixed", False):
                time_slot = self._get_time_slot(task["start_time"])
                time_distribution[time_slot] = time_distribution.get(time_slot, 0) + 1
        
        return {
            "total_scheduled": len(scheduled_tasks),
            "total_remaining": len(remaining_tasks),
            "total_duration_minutes": total_duration,
            "time_distribution": time_distribution,
            "is_valid": validation_result["is_valid"],
            "warnings": validation_result["warnings"]
        }
    
    def _get_time_slot(self, time_str: str) -> str:
        """根据时间获取时间段"""
        hour = int(time_str.split(":")[0])
        
        if 6 <= hour < 12:
            return "早晨"
        elif 12 <= hour < 18:
            return "下午"
        elif 18 <= hour < 22:
            return "傍晚"
        else:
            return "晚上"
    
    def print_schedule(self, result: Dict[str, Any]):
        """打印格式化的日程表"""
        print("\n" + "="*60)
        print("个人日程表")
        print("="*60)
        
        schedule = result["schedule"]
        scheduled_tasks = schedule["scheduled_tasks"]
        
        print(f"{'时间':<12} {'任务':<15} {'时长':<8} {'优先级':<6}")
        print("-" * 60)
        
        for task in scheduled_tasks:
            time_range = f"{task['start_time']}-{task['end_time']}"
            duration_str = f"{task['duration']}分钟"
            priority_str = f"P{task['priority']}" if task['priority'] > 0 else "固定"
            
            print(f"{time_range:<12} {task['task']:<15} {duration_str:<8} {priority_str:<6}")
        
        # 显示未安排的任务
        if schedule["remaining_tasks"]:
            print("\n未安排的任务:")
            for task in schedule["remaining_tasks"]:
                print(f"  - {task['task']}: {task['duration']}分钟")
        
        # 显示摘要
        summary = result["summary"]
        print(f"\n摘要:")
        print(f"  - 已安排任务: {summary['total_scheduled']} 个")
        print(f"  - 未安排任务: {summary['total_remaining']} 个")
        print(f"  - 总时长: {summary['total_duration_minutes']} 分钟")
        
        if summary["warnings"]:
            print(f"  - 警告: {', '.join(summary['warnings'])}")
    
    def generate_example_data(self, num_samples: int = 5) -> List[Dict[str, Any]]:
        """生成示例数据"""
        return self.data_generator.generate_dataset(num_samples)
    
    def interactive_mode(self):
        """交互模式"""
        print("欢迎使用个人日程生成系统!")
        print("输入 'quit' 退出，输入 'example' 查看示例")
        
        while True:
            try:
                user_input = input("\n请输入您的日程需求: ").strip()
                
                if user_input.lower() == 'quit':
                    print("再见!")
                    break
                
                if user_input.lower() == 'example':
                    examples = self.generate_example_data(3)
                    print("\n示例输入:")
                    for i, example in enumerate(examples, 1):
                        print(f"{i}. {example['input_text']}")
                    continue
                
                if not user_input:
                    print("请输入有效的日程需求")
                    continue
                
                # 生成日程
                result = self.generate_schedule(user_input)
                
                # 打印结果
                self.print_schedule(result)
                
            except KeyboardInterrupt:
                print("\n\n再见!")
                break
            except Exception as e:
                print(f"发生错误: {e}")

def main():
    """主函数"""
    print("个人日程生成系统")
    print("="*50)
    
    # 检查是否有训练好的模型
    model_path = "models/best_model"
    if not os.path.exists(model_path):
        print("未找到训练好的模型，将使用预训练模型")
        print("如需更好的效果，请先运行训练脚本")
        model_path = None
    
    # 初始化系统
    generator = PersonalScheduleGenerator(model_path)
    
    # 运行交互模式
    generator.interactive_mode()

if __name__ == "__main__":
    main()
