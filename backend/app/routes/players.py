from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_players():
    # Placeholder - Replace with actual logic
    return {"message": "Players route working"}
