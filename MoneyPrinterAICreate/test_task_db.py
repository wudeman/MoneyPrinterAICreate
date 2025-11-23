import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.config.database import engine, Base, get_db
from app.models.task_model import Task as TaskModel, TaskStatus
from app.models.task_schema import TaskCreate
from app.services.task_service import TaskService


def test_task_creation_and_query():
    """测试任务创建和查询功能"""
    print("开始测试任务表数据库功能...")
    
    # 创建数据库会话
    db: Session = next(get_db())
    
    try:
        # 1. 查询现有任务数量
        existing_tasks = db.query(TaskModel).count()
        print(f"当前数据库中的任务数量: {existing_tasks}")
        
        # 2. 如果没有任务，创建一个测试任务
        if existing_tasks == 0:
            print("创建测试任务...")
            task_data = TaskCreate(
                video_idea="测试视频创意",
                template_id=1,
                style_id=2,
                aspect_ratio="16:9",
                duration=60,
                operator="test_user"
            )
            
            # 直接使用SQLAlchemy创建任务
            print("使用原始方式创建任务...")
            db_task = TaskModel(
                video_idea=task_data.video_idea,
                template_id=task_data.template_id,
                style_id=task_data.style_id,
                aspect_ratio=task_data.aspect_ratio or "16:9",
                duration=task_data.duration or 30,
                status=TaskStatus.SCRIPT_COMPLETED.value,  # 使用枚举中实际存在的值
                operator=task_data.operator
            )
            db.add(db_task)
            db.commit()
            db.refresh(db_task)
            
            print(f"成功创建测试任务，ID: {db_task.id}")
            print(f"任务状态: {db_task.status} ({TaskStatus(db_task.status).name})")
            
            # 3. 测试查询功能
            queried_task = db.query(TaskModel).filter(TaskModel.id == db_task.id).first()
            if queried_task:
                print(f"\n查询到的任务信息:")
                print(f"- ID: {queried_task.id}")
                print(f"- 视频创意: {queried_task.video_idea}")
                print(f"- 模板ID: {queried_task.template_id}")
                print(f"- 风格ID: {queried_task.style_id}")
                print(f"- 宽高比: {queried_task.aspect_ratio}")
                print(f"- 时长: {queried_task.duration}")
                print(f"- 状态: {queried_task.status} ({TaskStatus(queried_task.status).name})")
                print(f"- 操作人: {queried_task.operator}")
                print(f"- 创建时间: {queried_task.created_at}")
            else:
                print("查询任务失败!")
        else:
            # 显示最新的5个任务
            recent_tasks = db.query(TaskModel).order_by(TaskModel.created_at.desc()).limit(5).all()
            print(f"\n显示最新的{len(recent_tasks)}个任务:")
            
            for i, task in enumerate(recent_tasks, 1):
                print(f"\n任务 {i}:")
                print(f"- ID: {task.id}")
                print(f"- 视频创意: {task.video_idea}")
                print(f"- 状态: {task.status} ({TaskStatus(task.status).name if task.status else '未知'})")
                print(f"- 剧本内容: {'已生成' if task.script else '未生成'}")
                print(f"- 创建时间: {task.created_at}")
        
        print("\n数据库验证测试完成!")
        return True
        
    except Exception as e:
        import traceback
        print(f"测试过程中发生错误: {str(e)}")
        print("详细错误栈:")
        traceback.print_exc()
        return False
    
    finally:
        db.close()


if __name__ == "__main__":
    test_task_creation_and_query()