"""
数据生成器 - 生成训练和验证数据
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

class DataGenerator:
    def __init__(self):
        self.task_templates = [
            "写周报", "健身", "开会", "学习", "阅读", "写作", "编程", "设计",
            "购物", "做饭", "打扫", "洗衣服", "看电影", "听音乐", "散步",
            "冥想", "瑜伽", "游泳", "跑步", "骑自行车", "画画", "摄影"
        ]
        
        self.time_preferences = ["早晨", "上午", "下午", "傍晚", "晚上"]
        self.priorities = ["紧急重要", "重要", "一般", "低优先级"]
        self.locations = ["在家", "公司", "健身房", "图书馆", "咖啡厅", "户外"]
        self.weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        
    def generate_single_sample(self) -> Dict[str, Any]:
        """生成单个训练样本"""
        # 随机选择上下文信息
        weekday = random.choice(self.weekdays)
        location = random.choice(self.locations)
        
        # 生成1-4个任务
        num_tasks = random.randint(1, 4)
        tasks = []
        
        for _ in range(num_tasks):
            task = random.choice(self.task_templates)
            duration = random.choice([30, 60, 90, 120, 180, 240])  # 分钟
            pref_time = random.choice(self.time_preferences)
            priority = random.choice(self.priorities)
            
            tasks.append({
                "task": task,
                "duration": duration,
                "pref_time": pref_time,
                "priority": self.get_priority_level(priority)
            })
        
        # 构建输入文本
        input_text = f"上下文：{weekday} {location} ｜ 需求："
        task_descriptions = []
        for task in tasks:
            hours = task["duration"] // 60
            minutes = task["duration"] % 60
            if hours > 0:
                time_str = f"{hours}小时"
                if minutes > 0:
                    time_str += f"{minutes}分钟"
            else:
                time_str = f"{minutes}分钟"
            
            task_descriptions.append(f"{task['task']}{time_str}")
        
        input_text += "，".join(task_descriptions)
        
        return {
            "input_text": input_text,
            "output_tasks": tasks
        }
    
    def get_priority_level(self, priority_name: str) -> int:
        """获取优先级数值"""
        priority_map = {
            "紧急重要": 1,
            "重要": 2,
            "一般": 3,
            "低优先级": 4
        }
        return priority_map.get(priority_name, 3)
    
    def generate_dataset(self, num_samples: int) -> List[Dict[str, Any]]:
        """生成完整数据集"""
        dataset = []
        for _ in range(num_samples):
            sample = self.generate_single_sample()
            dataset.append(sample)
        return dataset
    
    def save_dataset(self, dataset: List[Dict[str, Any]], filepath: str):
        """保存数据集到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    def load_dataset(self, filepath: str) -> List[Dict[str, Any]]:
        """从文件加载数据集"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

def main():
    """生成训练和验证数据"""
    generator = DataGenerator()
    
    # 创建数据目录
    import os
    os.makedirs("data", exist_ok=True)
    
    # 生成训练数据
    print("生成训练数据...")
    train_data = generator.generate_dataset(1000)
    generator.save_dataset(train_data, "data/train_data.json")
    
    # 生成验证数据
    print("生成验证数据...")
    val_data = generator.generate_dataset(200)
    generator.save_dataset(val_data, "data/val_data.json")
    
    print(f"训练数据: {len(train_data)} 样本")
    print(f"验证数据: {len(val_data)} 样本")
    
    # 显示示例
    print("\n训练数据示例:")
    print(json.dumps(train_data[0], ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
