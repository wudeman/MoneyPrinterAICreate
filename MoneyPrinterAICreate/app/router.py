"""Application configuration - root APIRouter.

Defines all FastAPI application endpoints.

Resources:
    1. https://fastapi.tiangolo.com/tutorial/bigger-applications

"""

from fastapi import APIRouter
from app.controllers.v1 import video, llm_model_controller, llm, template_controller, dict_controller

api_v1_router = APIRouter()
# api_v1_router.include_router(ping.router, tags=["ping"])
# api_v1_router.include_router(task.router, tags=["task"])
api_v1_router.include_router(llm.router, tags=["大模型服务"])
api_v1_router.include_router(video.router, tags=["video"])
api_v1_router.include_router(llm_model_controller.router, tags=["大模型管理"])
api_v1_router.include_router(template_controller.router, prefix="/templates", tags=["模板管理"])
api_v1_router.include_router(dict_controller.router, prefix="/dicts", tags=["字典管理"])

root_api_router = APIRouter()
root_api_router.include_router(api_v1_router, prefix="/api/v1")
