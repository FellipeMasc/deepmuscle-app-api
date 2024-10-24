from fastapi import APIRouter

from api.routes.sign_up import auth_router

api_router = APIRouter()
api_router.include_router(auth_router)
