from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class TaskDTO:
    """Data Transfer Object for Task entity"""
    id: Optional[int] = None
    title: str = ""
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str = ""
    created_at: Optional[datetime] = None
    update_task: Optional[datetime] = None