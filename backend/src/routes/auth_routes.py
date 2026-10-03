from fastapi import APIRouter

from src.controllers.auth_controller import login_controller

router = APIRouter(prefix="/api/auth", tags=["Auth"])
router.post("/login")(login_controller)
