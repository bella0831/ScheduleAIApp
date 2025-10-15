"""
配置文件 - 个人日程生成系统
"""

class Config:
    # 模型配置
    MODEL_NAME = "t5-small"  # 使用较小的模型以减少内存占用
    MAX_LENGTH = 512
    BATCH_SIZE = 8
    LEARNING_RATE = 3e-5
    NUM_EPOCHS = 10
    WARMUP_STEPS = 500
    
    # 数据配置
    TRAIN_DATA_PATH = "data/train_data.json"
    VAL_DATA_PATH = "data/val_data.json"
    OUTPUT_DIR = "models/"
    
    # 日程配置
    SLEEP_START = "22:00"  # 睡眠开始时间
    SLEEP_END = "06:00"    # 睡眠结束时间
    MAX_TASKS_PER_DAY = 8  # 每日最大任务数
    WORK_START = "09:00"   # 工作开始时间
    WORK_END = "18:00"     # 工作结束时间
    
    # 时间段定义
    TIME_SLOTS = {
        "早晨": ("06:00", "12:00"),
        "上午": ("09:00", "12:00"),
        "下午": ("12:00", "18:00"),
        "傍晚": ("18:00", "21:00"),
        "晚上": ("21:00", "22:00")
    }
    
    # 任务优先级
    PRIORITY_LEVELS = {
        "紧急重要": 1,
        "重要": 2,
        "一般": 3,
        "低优先级": 4
    }
    
    # 固定任务
    FIXED_TASKS = {
        "睡眠": {"start": "22:00", "end": "06:00", "duration": 480},
        "早餐": {"start": "07:00", "end": "08:00", "duration": 60},
        "午餐": {"start": "12:00", "end": "13:00", "duration": 60},
        "晚餐": {"start": "18:00", "end": "19:00", "duration": 60}
    }
