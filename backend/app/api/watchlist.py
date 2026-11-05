from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.watchlist import WatchlistItem
from app.schemas.watchlist import WatchlistItemCreate, WatchlistItemResponse
from app.core.security import get_optional_current_user

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


@router.get("", response_model=List[WatchlistItemResponse])
def get_watchlist(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    user_id = current_user.id if current_user else None
    items = (
        db.query(WatchlistItem)
        .filter(WatchlistItem.user_id == user_id)
        .order_by(WatchlistItem.added_at.desc())
        .all()
    )
    return [WatchlistItemResponse.model_validate(item) for item in items]


@router.post("", response_model=WatchlistItemResponse, status_code=status.HTTP_201_CREATED)
def add_to_watchlist(
    item_in: WatchlistItemCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    user_id = current_user.id if current_user else None
    upper_symbol = item_in.symbol.upper().strip()

    # Check if duplicate exists for this user
    existing = (
        db.query(WatchlistItem)
        .filter(WatchlistItem.user_id == user_id, WatchlistItem.symbol == upper_symbol)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{upper_symbol} is already in the watchlist.",
        )

    new_item = WatchlistItem(
        user_id=user_id,
        symbol=upper_symbol,
        name=item_in.name or f"{upper_symbol} Corporation",
        sector=item_in.sector or "Diversified",
        notes=item_in.notes,
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return WatchlistItemResponse.model_validate(new_item)


@router.delete("/{symbol}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_watchlist(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    user_id = current_user.id if current_user else None
    upper_symbol = symbol.upper().strip()

    item = (
        db.query(WatchlistItem)
        .filter(WatchlistItem.user_id == user_id, WatchlistItem.symbol == upper_symbol)
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Symbol {upper_symbol} not found in watchlist.",
        )

    db.delete(item)
    db.commit()
    return None
