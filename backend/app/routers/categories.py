from fastapi import APIRouter

from app.services.categorize import CATEGORY_RULES

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[str])
def list_categories():
    """Known category names, for populating a correction UI's options."""
    return list(CATEGORY_RULES.keys())
