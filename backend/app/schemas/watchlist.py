import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class WatchlistItemBase(BaseModel):
    symbol: str
    name: Optional[str] = None
    sector: Optional[str] = None
    notes: Optional[str] = None


class WatchlistItemCreate(WatchlistItemBase):
    pass


class WatchlistItemResponse(BaseModel):
    id: int
    symbol: str
    name: str
    sector: str
    notes: Optional[str] = None
    added_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
