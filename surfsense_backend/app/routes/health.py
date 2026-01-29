from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "kitab-backend"}

@router.get("/")
async def root():
    return {"message": "Kitab API", "status": "running"}
