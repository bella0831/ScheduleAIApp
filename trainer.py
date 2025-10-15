"""
模型训练器 - 训练T5模型
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from transformers import T5ForConditionalGeneration, T5Tokenizer, AdamW, get_linear_schedule_with_warmup
from model import ScheduleT5Model, ScheduleDataset
from data_generator import DataGenerator
from config import Config
import json
import os
from tqdm import tqdm
import numpy as np
from typing import List, Dict, Any

class ScheduleTrainer:
    """日程模型训练器"""
    
    def __init__(self, config: Config):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"使用设备: {self.device}")
        
        # 初始化模型
        self.model = ScheduleT5Model(config.MODEL_NAME)
        self.model.model.to(self.device)
        
        # 创建输出目录
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        
    def prepare_data(self):
        """准备训练和验证数据"""
        print("准备数据...")
        
        # 检查数据文件是否存在
        if not os.path.exists(self.config.TRAIN_DATA_PATH):
            print("生成训练数据...")
            generator = DataGenerator()
            generator.generate_dataset(1000)
            generator.save_dataset(generator.generate_dataset(1000), self.config.TRAIN_DATA_PATH)
        
        if not os.path.exists(self.config.VAL_DATA_PATH):
            print("生成验证数据...")
            generator = DataGenerator()
            generator.save_dataset(generator.generate_dataset(200), self.config.VAL_DATA_PATH)
        
        # 加载数据
        with open(self.config.TRAIN_DATA_PATH, 'r', encoding='utf-8') as f:
            train_data = json.load(f)
        
        with open(self.config.VAL_DATA_PATH, 'r', encoding='utf-8') as f:
            val_data = json.load(f)
        
        # 创建数据集
        self.train_dataset = ScheduleDataset(
            train_data, 
            self.model.tokenizer, 
            self.config.MAX_LENGTH
        )
        self.val_dataset = ScheduleDataset(
            val_data, 
            self.model.tokenizer, 
            self.config.MAX_LENGTH
        )
        
        # 创建数据加载器
        self.train_loader = DataLoader(
            self.train_dataset,
            batch_size=self.config.BATCH_SIZE,
            shuffle=True,
            num_workers=0
        )
        self.val_loader = DataLoader(
            self.val_dataset,
            batch_size=self.config.BATCH_SIZE,
            shuffle=False,
            num_workers=0
        )
        
        print(f"训练数据: {len(train_data)} 样本")
        print(f"验证数据: {len(val_data)} 样本")
    
    def train(self):
        """训练模型"""
        print("开始训练...")
        
        # 优化器和学习率调度器
        optimizer = AdamW(
            self.model.model.parameters(),
            lr=self.config.LEARNING_RATE,
            weight_decay=0.01
        )
        
        total_steps = len(self.train_loader) * self.config.NUM_EPOCHS
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=self.config.WARMUP_STEPS,
            num_training_steps=total_steps
        )
        
        # 训练循环
        best_val_loss = float('inf')
        train_losses = []
        val_losses = []
        
        for epoch in range(self.config.NUM_EPOCHS):
            print(f"\nEpoch {epoch + 1}/{self.config.NUM_EPOCHS}")
            
            # 训练阶段
            self.model.model.train()
            train_loss = 0.0
            train_progress = tqdm(self.train_loader, desc="训练")
            
            for batch in train_progress:
                # 将数据移到设备
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                labels = batch["labels"].to(self.device)
                
                # 前向传播
                outputs = self.model.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                loss = outputs.loss
                train_loss += loss.item()
                
                # 反向传播
                optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
                
                # 更新进度条
                train_progress.set_postfix({"loss": f"{loss.item():.4f}"})
            
            avg_train_loss = train_loss / len(self.train_loader)
            train_losses.append(avg_train_loss)
            
            # 验证阶段
            val_loss = self.evaluate()
            val_losses.append(val_loss)
            
            print(f"训练损失: {avg_train_loss:.4f}, 验证损失: {val_loss:.4f}")
            
            # 保存最佳模型
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                self.save_model(f"{self.config.OUTPUT_DIR}/best_model")
                print(f"保存最佳模型，验证损失: {val_loss:.4f}")
        
        # 保存最终模型
        self.save_model(f"{self.config.OUTPUT_DIR}/final_model")
        
        # 保存训练历史
        self.save_training_history(train_losses, val_losses)
        
        print("训练完成!")
    
    def evaluate(self) -> float:
        """评估模型"""
        self.model.model.eval()
        val_loss = 0.0
        
        with torch.no_grad():
            for batch in tqdm(self.val_loader, desc="验证"):
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                labels = batch["labels"].to(self.device)
                
                outputs = self.model.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                val_loss += outputs.loss.item()
        
        return val_loss / len(self.val_loader)
    
    def save_model(self, save_path: str):
        """保存模型"""
        self.model.save_model(save_path)
        print(f"模型已保存到: {save_path}")
    
    def save_training_history(self, train_losses: List[float], val_losses: List[float]):
        """保存训练历史"""
        history = {
            "train_losses": train_losses,
            "val_losses": val_losses
        }
        
        with open(f"{self.config.OUTPUT_DIR}/training_history.json", 'w') as f:
            json.dump(history, f, indent=2)
    
    def test_model(self, test_inputs: List[str]):
        """测试模型"""
        print("\n测试模型...")
        self.model.model.eval()
        
        for input_text in test_inputs:
            print(f"\n输入: {input_text}")
            
            # 生成输出
            output_text = self.model.generate(input_text)
            print(f"输出: {output_text}")
            
            # 解析任务
            tasks = self.model.parse_output(output_text)
            print("解析的任务:")
            for task in tasks:
                print(f"  - {task['task']}: {task['duration']}分钟, {task['pref_time']}, 优先级{task['priority']}")

def main():
    """主训练函数"""
    config = Config()
    trainer = ScheduleTrainer(config)
    
    # 准备数据
    trainer.prepare_data()
    
    # 训练模型
    trainer.train()
    
    # 测试模型
    test_inputs = [
        "上下文：周三 在家 ｜ 需求：写周报2小时，健身1小时，下午开会",
        "上下文：周五 公司 ｜ 需求：学习编程3小时，阅读1小时",
        "上下文：周六 在家 ｜ 需求：打扫卫生1小时，看电影2小时，散步30分钟"
    ]
    
    trainer.test_model(test_inputs)

if __name__ == "__main__":
    main()
