from fastapi import APIRouter

router = APIRouter()

from . import tasks  # Import after router is defined to avoid circular imports