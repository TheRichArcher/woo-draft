from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_draft_info():
    # Placeholder - Replace with actual logic
    return {"message": "Draft route working"}
