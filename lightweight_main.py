"""
轻量级个人日程生成系统 - 使用规则解析替代T5模型
"""

import re
from typing import List, Dict, Any
from config import Config
from scheduler import ScheduleRuleEngine

class RuleBasedParser:
    """基于规则的文本解析器"""
    
    def __init__(self):
        self.time_patterns = {
            r'(\d+)小时': lambda x: int(x) * 60,
            r'(\d+)分钟': lambda x: int(x),
            r'(\d+)h': lambda x: int(x) * 60,
            r'(\d+)min': lambda x: int(x)
        }
        
        self.time_preferences = {
            '早晨': ['早晨', '早上', '早'],
            '上午': ['上午'],
            '下午': ['下午', '午后'],
            '傍晚': ['傍晚', '黄昏'],
            '晚上': ['晚上', '夜晚', '晚']
        }
       
        
        self.priority_keywords = {
            1: ['紧急', '重要', '必须', '关键'],
            2: ['重要', '需要', '应该'],
            3: ['一般', '普通', '可以'],
            4: ['低', '不紧急', '可选']
        }
    
    def parse_tasks(self, input_text: str) -> List[Dict[str, Any]]:
        """解析输入文本为任务列表"""
        tasks = []
        
        # 提取任务描述
        task_descriptions = self._extract_task_descriptions(input_text)
        
        for desc in task_descriptions:
            task = self._parse_single_task(desc)
            if task:
                tasks.append(task)
        
        return tasks
    
    def _extract_task_descriptions(self, text: str) -> List[str]:
        """提取任务描述"""
        # 简单的分割方法
        separators = ['，', ',', '、', '；', ';']
        for sep in separators:
            if sep in text:
                return [t.strip() for t in text.split(sep) if t.strip()]
        
        return [text.strip()]
    
    def _parse_single_task(self, task_text: str) -> Dict[str, Any]:
        """解析单个任务"""
        # 提取任务名称
        task_name = self._extract_task_name(task_text)
        
        # 提取时长
        duration = self._extract_duration(task_text)
        
        # 提取时间偏好
        pref_time = self._extract_time_preference(task_text)
        
        # 提取优先级
        priority = self._extract_priority(task_text)
        
        return {
            "task": task_name,
            "duration": duration,
            "pref_time": pref_time,
            "priority": priority
        }
    
    def _extract_task_name(self, text: str) -> str:
        """提取任务名称"""
        # 移除时长和时间信息
        cleaned = text
        for pattern in self.time_patterns.keys():
            cleaned = re.sub(pattern, '', cleaned)
        
        # 移除时间偏好词
        for prefs in self.time_preferences.values():
            for pref in prefs:
                cleaned = cleaned.replace(pref, '')
        
        # 移除优先级词
        for keywords in self.priority_keywords.values():
            for keyword in keywords:
                cleaned = cleaned.replace(keyword, '')
        
        return cleaned.strip()
    
    def _extract_duration(self, text: str) -> int:
        """提取任务时长（分钟）"""
        for pattern, converter in self.time_patterns.items():
            match = re.search(pattern, text)
            if match:
                return converter(match.group(1))
        
        # 默认时长
        return 60
    
    def _extract_time_preference(self, text: str) -> str:
        """提取时间偏好"""
        for pref, keywords in self.time_preferences.items():
            for keyword in keywords:
                if keyword in text:
                    return pref
        
        # 默认偏好
        return "上午"
    
    def _extract_priority(self, text: str) -> int:
        """提取优先级"""
        for priority, keywords in self.priority_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return priority
        
        # 默认优先级
        return 3

class LightweightScheduleGenerator:
    """轻量级日程生成器"""
    
    def __init__(self):
        self.config = Config
        self.parser = RuleBasedParser()
        self.scheduler = ScheduleRuleEngine(self.config)
    
    def generate_schedule(self, input_text: str) -> Dict[str, Any]:
        """生成日程安排"""
        print(f"解析输入: {input_text}")
        
        # 解析任务
        tasks = self.parser.parse_tasks(input_text)
        print(f"解析结果: {len(tasks)} 个任务")
        
        # 调度任务
        schedule_result = self.scheduler.schedule_tasks(tasks)
        print(f"调度结果: {schedule_result['total_scheduled']} 个任务")
        
        # 验证日程
        validation = self.scheduler.validate_schedule(schedule_result)
        
        return {
            "input": input_text,
            "parsed_tasks": tasks,
            "schedule": schedule_result,
            "validation": validation
        }
    
    def print_schedule(self, result: Dict[str, Any]):
        """打印日程安排"""
        print("\n" + "="*60)
        print("📅 个人日程安排")
        print("="*60)
        
        print(f"📝 输入: {result['input']}")
        print(f"🔍 解析任务数: {len(result['parsed_tasks'])}")
        print(f"⏰ 安排任务数: {result['schedule']['total_scheduled']}")
        
        print("\n📋 解析的任务:")
        for i, task in enumerate(result['parsed_tasks'], 1):
            print(f"  {i}. {task['task']} ({task['duration']}分钟, {task['pref_time']}, 优先级{task['priority']})")
        
        print("\n⏰ 日程安排:")
        for item in result['schedule']['scheduled_tasks']:
            print(f"  {item['start_time']}-{item['end_time']}: {item['task']}")
        
        if result['schedule']['remaining_tasks']:
            print(f"\n⚠️  未安排的任务: {len(result['schedule']['remaining_tasks'])} 个")
            for task in result['schedule']['remaining_tasks']:
                print(f"  - {task['task']} ({task['duration']}分钟)")
        
        if 'validation' in result:
            print(f"\n✅ 验证结果: {result['validation']['is_valid']}")
            if result['validation']['errors']:
                print(f"❌ 错误: {result['validation']['errors']}")
            if result['validation']['warnings']:
                print(f"⚠️  警告: {result['validation']['warnings']}")
        
        print("="*60)

def quick_demo():
    """快速演示"""
    print("轻量级个人日程生成系统 - 快速演示")
    print("="*50)
    
    generator = LightweightScheduleGenerator()
    
    demo_inputs = [
        "写周报2小时，健身1小时，下午开会",
        "学习编程3小时，阅读1小时，团队会议",
        "打扫卫生1小时，看电影2小时，散步30分钟"
    ]
    
    for i, input_text in enumerate(demo_inputs, 1):
        print(f"\n演示 {i}:")
        print("-" * 30)
        
        result = generator.generate_schedule(input_text)
        generator.print_schedule(result)

def interactive_demo():
    """交互式演示"""
    print("轻量级个人日程生成系统 - 交互式演示")
    print("="*50)
    print("输入您的日程需求，系统将自动生成日程安排")
    print("输入 'quit' 退出")
    print()
    
    generator = LightweightScheduleGenerator()
    
    while True:
        try:
            user_input = input("请输入日程需求: ").strip()
            
            if user_input.lower() == 'quit':
                print("再见!")
                break
            
            if not user_input:
                print("请输入有效的日程需求")
                continue
            
            result = generator.generate_schedule(user_input)
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
