"""
T5模型类 - 用于意图识别和任务解析
"""

import torch
print("Imported torch")
import torch.nn as nn
from transformers import T5ForConditionalGeneration, T5Tokenizer
print("Imported transformers")
from typing import List, Dict, Any, Optional
print("Imported typing")
import json
print("Imported json")

print("model.py imported")

class ScheduleT5Model:
    def __init__(self, model_name: str = "t5-base"):
        self.model_name = model_name
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)
        
        # 添加特殊token
        self.special_tokens = [
            "<task>", "</task>",
            "<duration>", "</duration>",
            "<time>", "</time>",
            "<priority>", "</priority>"
        ]
        self.tokenizer.add_tokens(self.special_tokens)
        self.model.resize_token_embeddings(len(self.tokenizer))
        
    def format_output(self, tasks: List[Dict[str, Any]]) -> str:
        """将任务列表格式化为输出文本"""
        output_parts = []
        for task in tasks:
            task_str = (
                f"<task>{task['task']}</task> "
                f"<duration>{task['duration']}</duration> "
                f"<time>{task['pref_time']}</time> "
                f"<priority>{task['priority']}</priority>"
            )
            output_parts.append(task_str)
        return " | ".join(output_parts)
    
    def parse_output(self, output_text: str) -> List[Dict[str, Any]]:
        """将模型生成的标注文本解析为任务列表，稳健处理缺失/异常字段。

        规则：
        - 使用 " | " 分隔多个任务块
        - 任务名/时长为必填，缺失或非法则跳过该块
        - 偏好时间缺失或为空默认 "上午"
        - 优先级缺失或非数字默认 3
        """
        tasks = []
        # 模型输出按分隔符拆分为多个任务块
        task_blocks = output_text.split(" | ")
        
        for block in task_blocks:
            try:
                # 提取任务名称
                task_start = block.find("<task>") + 6
                task_end = block.find("</task>")
                if task_start < 6 or task_end == -1:
                    # 块不包含有效的任务标签，跳过
                    continue
                task_name = block[task_start:task_end].strip()
                
                # 提取时长
                duration_start = block.find("<duration>") + 10
                duration_end = block.find("</duration>")
                if duration_start < 10 or duration_end == -1:
                    # 缺失时长则跳过该块
                    continue
                duration_str = block[duration_start:duration_end].strip()
                if duration_str == "":
                    # 空时长不合法，跳过
                    continue
                duration = int(duration_str)
                
                # 提取偏好时间
                time_start = block.find("<time>") + 6
                time_end = block.find("</time>")
                if time_start < 6 or time_end == -1:
                    pref_time = "上午"
                else:
                    pref_time = block[time_start:time_end].strip() or "上午"
                
                # 提取优先级
                priority_start = block.find("<priority>") + 10
                priority_end = block.find("</priority>")
                if priority_start < 10 or priority_end == -1:
                    priority = 3
                else:
                    priority_str = block[priority_start:priority_end].strip()
                    priority = int(priority_str) if priority_str.isdigit() else 3
                
                tasks.append({
                    "task": task_name,
                    "duration": duration,
                    "pref_time": pref_time,
                    "priority": priority
                })
            except (ValueError, IndexError) as e:
                print(f"解析任务块时出错: {block}, 错误: {e}")
                continue
        
        return tasks
    
    def encode_input(self, input_text: str) -> Dict[str, torch.Tensor]:
        """编码输入文本"""
        return self.tokenizer(
            input_text,
            max_length=512,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
    
    def encode_output(self, output_text: str) -> Dict[str, torch.Tensor]:
        """编码输出文本"""
        return self.tokenizer(
            output_text,
            max_length=512,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
    
    def generate(self, input_text: str, max_length: int = 512) -> str:
        """生成任务解析结果"""
        inputs = self.encode_input(input_text)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_beams=4,
                early_stopping=True,
                no_repeat_ngram_size=2
            )
        
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    def predict_tasks(self, input_text: str) -> List[Dict[str, Any]]:
        """预测任务列表"""
        output_text = self.generate(input_text)
        return self.parse_output(output_text)
    
    def save_model(self, save_path: str):
        """保存模型"""
        self.model.save_pretrained(save_path)
        self.tokenizer.save_pretrained(save_path)
    
    def load_model(self, load_path: str):
        """加载模型"""
        self.model = T5ForConditionalGeneration.from_pretrained(load_path)
        self.tokenizer = T5Tokenizer.from_pretrained(load_path)

class ScheduleDataset(torch.utils.data.Dataset):
    """自定义数据集类"""
    
    def __init__(self, data: List[Dict[str, Any]], tokenizer, max_length: int = 512):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length
        
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        
        # 编码输入
        input_encoding = self.tokenizer(
            item["input_text"],
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        # 格式化输出
        model = ScheduleT5Model()
        output_text = model.format_output(item["output_tasks"])
        
        # 编码输出
        target_encoding = self.tokenizer(
            output_text,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        return {
            "input_ids": input_encoding["input_ids"].squeeze(),
            "attention_mask": input_encoding["attention_mask"].squeeze(),
            "labels": target_encoding["input_ids"].squeeze()
        }
