from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Task:
    id: int
    name: str
    tag: str
    planned_duration_minutes: Optional[int]
    created_at: datetime
    is_active: bool
    color: Optional[str] = None

