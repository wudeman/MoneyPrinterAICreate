from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.task_model import Task, TaskStatus
from app.models.task_schema import TaskCreate, TaskUpdate, TaskResponse


class TaskService:
    """任务服务类"""
    
    @staticmethod
    def create_task(db: Session, task_data: TaskCreate) -> Task:
        """创建新任务"""
        # 创建任务实例
        task_dict = task_data.model_dump()
        
        # 初始状态设为剧本生成中
        task_dict['status'] = TaskStatus.SCRIPT_GENERATING.value
        
        # 设置默认值
        if 'operator' not in task_dict or not task_dict['operator']:
            task_dict['operator'] = "system"
        if 'aspect_ratio' not in task_dict or not task_dict['aspect_ratio']:
            task_dict['aspect_ratio'] = "16:9"
        if 'duration' not in task_dict or not task_dict['duration']:
            task_dict['duration'] = 30
        
        db_task = Task(**task_dict)
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    
    @staticmethod
    def get_task(db: Session, task_id: int) -> Optional[Task]:
        """根据ID获取任务"""
        return db.query(Task).filter(Task.id == task_id).first()
    
    @staticmethod
    def update_task(db: Session, task_id: int, task_update: TaskUpdate) -> Task:
        """更新任务信息"""
        db_task = TaskService.get_task(db, task_id)
        if not db_task:
            raise ValueError(f"Task with id {task_id} not found")
        
        update_data = task_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)
        
        db.commit()
        db.refresh(db_task)
        return db_task
    
    @staticmethod
    def get_tasks_by_operator(db: Session, operator: str, skip: int = 0, limit: int = 100) -> List[Task]:
        """根据操作人获取任务列表"""
        return db.query(Task).filter(Task.operator == operator).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_all_tasks(db: Session, skip: int = 0, limit: int = 100) -> List[Task]:
        """获取所有任务列表"""
        return db.query(Task).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_task_status(db: Session, task_id: int, status: TaskStatus) -> Task:
        """更新任务状态"""
        db_task = TaskService.get_task(db, task_id)
        if not db_task:
            raise ValueError(f"Task with id {task_id} not found")
        
        db_task.status = status.value
        db.commit()
        db.refresh(db_task)
        return db_task
    
    @staticmethod
    def save_script_to_task(db: Session, task_id: int, script: str) -> Task:
        """保存剧本到任务"""
        return TaskService.update_task(db, task_id, TaskUpdate(script=script))