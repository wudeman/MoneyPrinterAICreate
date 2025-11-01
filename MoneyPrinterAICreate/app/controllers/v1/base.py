from fastapi import APIRouter, Depends


def new_router(dependencies=None):
    router = APIRouter()
    router.tags = ["V1"]
    # 移除重复的前缀，因为在router.py中已经添加了"/api/v1"
    # router.prefix = "/api/v1"
    # 将认证依赖项应用于所有路由
    if dependencies:
        router.dependencies = dependencies
    return router
