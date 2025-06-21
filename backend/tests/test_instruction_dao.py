import asyncio
from backend.dao.InstructionDao import InstructionDao
from backend.agent.models import Instruction

async def main():
    dao = InstructionDao()
    
    # 测试获取用户偏好说明
    print("=== 测试 get_by_id ===")
    instructions = await dao.get_by_id('1')
    print(f"用户偏好说明数量: {len(instructions)}")
    for instruction in instructions:
        print(f"偏好说明: {instruction}")
    
    # 测试创建偏好说明
    print("\n=== 测试 create_instruction ===")
    new_instruction = Instruction(
        content="请使用简洁明了的语言回复",
        language="zh"
    )
    success = await dao.create_instruction('1', new_instruction)
    print(f"创建结果: {success}")
    
    # 测试按key更新偏好说明
    print("\n=== 测试 update_by_key ===")
    updated_instruction = Instruction(
        content="请使用简洁明了的语言回复，并提供具体的例子",
        language="zh"
    )
    # 使用正确的key格式，与create_instruction中生成的key一致
    key = "1_zh"
    success = await dao.update_by_key('1', key, updated_instruction)
    print(f"更新结果: {success}")
    
    # 再次获取验证更新
    print("\n=== 验证更新结果 ===")
    instructions = await dao.get_by_id('1')
    for instruction in instructions:
        if instruction.language == 'zh':
            print(f"更新后的偏好说明: {instruction}")
    
    # 测试按key删除偏好说明
    print("\n=== 测试 delete_by_key ===")
    success = await dao.delete_by_key('1', key)
    print(f"删除结果: {success}")
    
    # 再次获取验证删除
    print("\n=== 验证删除结果 ===")
    instructions = await dao.get_by_id('1')
    print(f"删除后的偏好说明数量: {len(instructions)}")

if __name__ == '__main__':
    asyncio.run(main())