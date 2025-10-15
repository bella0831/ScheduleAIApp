"""
规则引擎 - 处理日程安排和约束
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import copy

class TimeSlot:
    """时间段类"""
    def __init__(self, start_time: str, end_time: str, task: str = None):
        self.start_time = start_time
        self.end_time = end_time
        self.task = task
        self.duration = self._calculate_duration()
    
    def _calculate_duration(self) -> int:
        """计算时间段时长（分钟）"""
        start = datetime.strptime(self.start_time, "%H:%M")
        end = datetime.strptime(self.end_time, "%H:%M")
        if end < start:  # 跨天情况
            end += timedelta(days=1)
        return int((end - start).total_seconds() / 60)
    
    def overlaps_with(self, other: 'TimeSlot') -> bool:
        """检查是否与另一个时间段重叠"""
        start1 = datetime.strptime(self.start_time, "%H:%M")
        end1 = datetime.strptime(self.end_time, "%H:%M")
        if end1 < start1:  # 跨天情况
            end1 += timedelta(days=1)
        
        start2 = datetime.strptime(other.start_time, "%H:%M")
        end2 = datetime.strptime(other.end_time, "%H:%M")
        if end2 < start2:  # 跨天情况
            end2 += timedelta(days=1)
        
        return start1 < end2 and start2 < end1
    
    def contains(self, time: str) -> bool:
        """检查是否包含指定时间"""
        check_time = datetime.strptime(time, "%H:%M")
        start = datetime.strptime(self.start_time, "%H:%M")
        end = datetime.strptime(self.end_time, "%H:%M")
        if end < start:  # 跨天情况
            end += timedelta(days=1)
            if check_time < start:
                check_time += timedelta(days=1)
        
        return start <= check_time <= end

class ScheduleRuleEngine:
    """日程规则引擎"""
    
    def __init__(self, config):
        self.config = config
        self.fixed_tasks = self._initialize_fixed_tasks()
        self.time_slots = config.TIME_SLOTS
        
    def _initialize_fixed_tasks(self) -> List[TimeSlot]:
        """初始化固定任务"""
        fixed_tasks = []
        for task_name, task_info in self.config.FIXED_TASKS.items():
            time_slot = TimeSlot(
                start_time=task_info["start"],
                end_time=task_info["end"],
                task=task_name
            )
            fixed_tasks.append(time_slot)
        return fixed_tasks
    
    def get_available_time_slots(self) -> List[TimeSlot]:
        """获取可用时间段"""
        # 创建24小时的时间段
        available_slots = []
        
        # 排除睡眠时间
        sleep_start = self.config.SLEEP_START
        sleep_end = self.config.SLEEP_END
        
        # 添加睡眠前的时间段
        if sleep_start != "00:00":
            available_slots.append(TimeSlot("00:00", sleep_start))
        
        # 添加睡眠后的时间段
        if sleep_end != "23:59":
            available_slots.append(TimeSlot(sleep_end, "23:59"))
        
        # 排除固定任务时间
        for fixed_task in self.fixed_tasks:
            if fixed_task.task not in ["睡眠"]:  # 排除睡眠，因为已经处理了
                available_slots = self._remove_overlapping_slots(available_slots, fixed_task)
        
        return available_slots
    
    def _remove_overlapping_slots(self, slots: List[TimeSlot], task: TimeSlot) -> List[TimeSlot]:
        """移除与任务重叠的时间段"""
        new_slots = []
        for slot in slots:
            if not slot.overlaps_with(task):
                new_slots.append(slot)
            else:
                # 分割重叠的时间段
                split_slots = self._split_slot(slot, task)
                new_slots.extend(split_slots)
        return new_slots
    
    def _split_slot(self, slot: TimeSlot, task: TimeSlot) -> List[TimeSlot]:
        """分割时间段"""
        split_slots = []
        
        slot_start = datetime.strptime(slot.start_time, "%H:%M")
        slot_end = datetime.strptime(slot.end_time, "%H:%M")
        task_start = datetime.strptime(task.start_time, "%H:%M")
        task_end = datetime.strptime(task.end_time, "%H:%M")
        
        # 处理跨天情况
        if slot_end < slot_start:
            slot_end += timedelta(days=1)
        if task_end < task_start:
            task_end += timedelta(days=1)
        
        # 添加任务前的时间段
        if slot_start < task_start:
            pre_slot = TimeSlot(
                slot.start_time,
                task.start_time
            )
            split_slots.append(pre_slot)
        
        # 添加任务后的时间段
        if task_end < slot_end:
            post_slot = TimeSlot(
                task.end_time,
                slot.end_time
            )
            split_slots.append(post_slot)
        
        return split_slots
    
    def find_best_time_slot(self, task: Dict[str, Any], available_slots: List[TimeSlot]) -> Optional[TimeSlot]:
        """为任务找到最佳时间段"""
        pref_time = task["pref_time"]
        duration = task["duration"]
        
        # 获取偏好时间段
        if pref_time in self.time_slots:
            pref_start, pref_end = self.time_slots[pref_time]
            pref_slot = TimeSlot(pref_start, pref_end)
        else:
            # 如果没有指定偏好时间，使用所有可用时间段
            return self._find_any_suitable_slot(task, available_slots)
        
        # 在偏好时间段内寻找合适的槽位
        suitable_slots = []
        for slot in available_slots:
            if slot.overlaps_with(pref_slot) and slot.duration >= duration:
                # 计算重叠部分
                overlap_start = max(slot.start_time, pref_slot.start_time)
                overlap_end = min(slot.end_time, pref_slot.end_time)
                overlap_slot = TimeSlot(overlap_start, overlap_end)
                
                if overlap_slot.duration >= duration:
                    suitable_slots.append((overlap_slot, slot))
        
        if suitable_slots:
            # 选择最接近偏好时间开始的槽位
            suitable_slots.sort(key=lambda x: x[0].start_time)
            return suitable_slots[0][1]
        
        # 如果偏好时间段没有合适槽位，在其他时间段寻找
        return self._find_any_suitable_slot(task, available_slots)
    
    def _find_any_suitable_slot(self, task: Dict[str, Any], available_slots: List[TimeSlot]) -> Optional[TimeSlot]:
        """在任何可用时间段中寻找合适的槽位"""
        duration = task["duration"]
        
        suitable_slots = [slot for slot in available_slots if slot.duration >= duration]
        
        if suitable_slots:
            # 按优先级排序：优先选择时长接近的槽位
            suitable_slots.sort(key=lambda x: abs(x.duration - duration))
            return suitable_slots[0]
        
        return None
    
    def schedule_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """安排任务到日程表"""
        # 按优先级排序任务
        sorted_tasks = sorted(tasks, key=lambda x: x["priority"])
        
        # 获取可用时间段
        available_slots = self.get_available_time_slots()
        
        scheduled_tasks = []
        remaining_tasks = []
        
        for task in sorted_tasks:
            if len(scheduled_tasks) >= self.config.MAX_TASKS_PER_DAY:
                remaining_tasks.append(task)
                continue
            
            # 寻找最佳时间段
            best_slot = self.find_best_time_slot(task, available_slots)
            
            if best_slot:
                # 安排任务
                scheduled_task = copy.deepcopy(task)
                scheduled_task["start_time"] = best_slot.start_time
                scheduled_task["end_time"] = self._calculate_end_time(
                    best_slot.start_time, task["duration"]
                )
                scheduled_tasks.append(scheduled_task)
                
                # 更新可用时间段
                task_slot = TimeSlot(
                    scheduled_task["start_time"],
                    scheduled_task["end_time"]
                )
                available_slots = self._remove_overlapping_slots(available_slots, task_slot)
            else:
                remaining_tasks.append(task)
        
        # 添加固定任务到日程表
        for fixed_task in self.fixed_tasks:
            scheduled_tasks.append({
                "task": fixed_task.task,
                "start_time": fixed_task.start_time,
                "end_time": fixed_task.end_time,
                "duration": fixed_task.duration,
                "priority": 0,  # 固定任务优先级最高
                "is_fixed": True
            })
        
        # 按开始时间排序
        scheduled_tasks.sort(key=lambda x: x["start_time"])
        
        return {
            "scheduled_tasks": scheduled_tasks,
            "remaining_tasks": remaining_tasks,
            "total_scheduled": len(scheduled_tasks),
            "total_remaining": len(remaining_tasks)
        }
    
    def _calculate_end_time(self, start_time: str, duration: int) -> str:
        """计算结束时间"""
        start = datetime.strptime(start_time, "%H:%M")
        end = start + timedelta(minutes=duration)
        return end.strftime("%H:%M")
    
    def validate_schedule(self, schedule: Dict[str, Any]) -> Dict[str, Any]:
        """验证日程表的有效性"""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        scheduled_tasks = schedule["scheduled_tasks"]
        
        # 检查任务重叠
        for i in range(len(scheduled_tasks)):
            for j in range(i + 1, len(scheduled_tasks)):
                task1 = scheduled_tasks[i]
                task2 = scheduled_tasks[j]
                
                slot1 = TimeSlot(task1["start_time"], task1["end_time"])
                slot2 = TimeSlot(task2["start_time"], task2["end_time"])
                
                if slot1.overlaps_with(slot2):
                    validation_result["is_valid"] = False
                    validation_result["errors"].append(
                        f"任务重叠: {task1['task']} 和 {task2['task']}"
                    )
        
        # 检查睡眠时间
        sleep_tasks = [task for task in scheduled_tasks if task["task"] == "睡眠"]
        if not sleep_tasks:
            validation_result["warnings"].append("未安排睡眠时间")
        elif len(sleep_tasks) > 1:
            validation_result["errors"].append("睡眠时间安排重复")
        
        # 检查任务数量
        non_fixed_tasks = [task for task in scheduled_tasks if not task.get("is_fixed", False)]
        if len(non_fixed_tasks) > self.config.MAX_TASKS_PER_DAY:
            validation_result["warnings"].append(
                f"任务数量超过限制: {len(non_fixed_tasks)} > {self.config.MAX_TASKS_PER_DAY}"
            )
        
        return validation_result
