"""Application configuration - root APIRouter.

Defines all FastAPI application endpoints.

Resources:
    1. https://fastapi.tiangolo.com/tutorial/bigger-applications

"""

from fastapi import APIRouter
from app.controllers.v1 import ping, task, video, llm_model_controller

api_v1_router = APIRouter()
api_v1_router.include_router(ping.router, tags=["ping"])
api_v1_router.include_router(task.router, tags=["task"])
api_v1_router.include_router(video.router, tags=["video"])
api_v1_router.include_router(llm_model_controller.router, tags=["大模型管理"])

api_router = APIRouter()
api_router.include_router(api_v1_router, prefix="/api/v1")
