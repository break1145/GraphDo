import asyncio
from backend.dao.ProfileDao import ProfileDao
from backend.agent.models import Profile

async def main():
    dao = ProfileDao()
    
    # 测试获取用户档案
    print("=== 测试 get_by_id ===")
    profile = await dao.get_by_id('1')
    if profile:
        print(f"用户档案: {profile}")
    else:
        print("未找到用户档案")
    
    # 测试创建用户档案
    print("\n=== 测试 create_profile ===")
    new_profile = Profile(
        name="张三",
        job="软件工程师",
        location="北京",
        interests=["编程","阅读"],
        connections=["同事","朋友"]
    )
    success = await dao.create_profile('2', new_profile)
    print(f"创建结果: {success}")
    
    # 测试更新用户档案
    print("\n=== 测试 update_profile ===")
    updated_profile = Profile(
        name="张三",
        job="高级软件工程师",
        location="上海",
        interests=["编程", "阅读", "123"],
        connections=["同事", "朋友", "456"]
    )
    success = await dao.update_profile('2', updated_profile)
    print(f"更新结果: {success}")
    
    # 再次获取验证更新
    print("\n=== 验证更新结果 ===")
    profile = await dao.get_by_id('2')
    if profile:
        print(f"更新后的用户档案: {profile}")

if __name__ == '__main__':
    asyncio.run(main())