from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.preferences import UserPreferences
from app.schemas.preferences import PreferencesUpdate, PreferencesResponse
from app.core.security import get_optional_current_user

router = APIRouter(prefix="/preferences", tags=["preferences"])


def get_or_create_preferences(db: Session, user: Optional[User] = None) -> UserPreferences:
    user_id = user.id if user else None
    prefs = db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
    if not prefs:
        prefs = UserPreferences(
            user_id=user_id,
            tracked_sectors=[
                "Banking & Financial Services",
                "Information Technology",
                "Automobile & Auto Ancillary",
            ],
            tracked_symbols=["RELIANCE", "TCS", "HDFCBANK", "INFY", "TATAMOTORS"],
            sentiment_alert_threshold=0.75,
            email_alerts=True,
            daily_digest=True,
            digest_time="08:30",
            enable_ai_suggestions=True,
        )
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    return prefs


@router.get("", response_model=PreferencesResponse)
def get_preferences(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    prefs = get_or_create_preferences(db, current_user)
    return PreferencesResponse.model_validate(prefs)


@router.put("", response_model=PreferencesResponse)
def update_preferences(
    update_data: PreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    prefs = get_or_create_preferences(db, current_user)

    for field, value in update_data.model_dump().items():
        setattr(prefs, field, value)

    db.commit()
    db.refresh(prefs)
    return PreferencesResponse.model_validate(prefs)
