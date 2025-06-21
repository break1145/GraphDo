import asyncio
from datetime import datetime
from backend.agent.models import ToDo
from backend.dao.ToDoDao import ToDoDao


async def main():
    dao = ToDoDao()
    
    # 测试获取待办事项
    print("=== 测试 get_by_id ===")
    todos = await dao.get_by_id('1')
    print(f"待办事项数量: {len(todos)}")
    for todo in todos:
        print(f"待办事项: {todo}")
    
    # 测试创建待办事项
    # {"task": "Finish the assignment and write the paper for the class by next Wednesday", "status": "not started", "deadline": "2025-06-25T23:59:59", "solutions": ["Complete the assignment for the class", "Write the paper for the class"], "planned_edits": [], "time_to_complete": 300}
    print("\n=== 测试 create_todo ===")
    new_todo = ToDo(
        task="完成项目文档",
        status="not started",
        deadline=datetime(year=2021, month=1, day=1),
        solutions=["使用Markdown格式编写"],
        planned_edits=["添加API文档和用户指南"],
        time_to_complete=300
    )
    success = await dao.create_todo('1', new_todo)
    print(f"创建结果: {success}")
    
    # 测试按key更新待办事项
    print("\n=== 测试 update_by_key ===")
    updated_todo = ToDo(
        task="完成项目文档",
        status="in progress",
        deadline=datetime(year=2021, month=3, day=2),
        solutions=["使用Markdown格式编写1212121212121212"],
        planned_edits=["添加API文档和用户指南"],
        time_to_complete=300
    )
    key = "1_完成项目文档"
    success = await dao.update_by_key('1', key, updated_todo)
    print(f"更新结果: {success}")
    
    # 测试按key删除待办事项
    print("\n=== 测试 delete_by_key ===")
    success = await dao.delete_by_key('1', key)
    print(f"删除结果: {success}")
    
    # 再次获取验证删除
    print("\n=== 验证删除结果 ===")
    todos = await dao.get_by_id('1')
    print(f"删除后的待办事项数量: {len(todos)}")

if __name__ == '__main__':
    asyncio.run(main())