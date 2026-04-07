from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date

class MathOnboardRequest(BaseModel):
    username: str
    exam_name: str = "考研数学一"
    target_score: int = 140
    exam_date: date
    daily_hours: int = 4
    resources_config: Dict[str, Any] = {}

class MathAttemptRequest(BaseModel):
    username: str
    problem_id: int
    self_score: int # 0-5
    time_spent_sec: int
    user_steps: str
    key_check_result: Dict[str, Any] = {}
    error_tags: List[str] = []

class MathTask(BaseModel):
    id: str
    type: str # review, new_knowledge, practice, recap
    content: str
    duration_min: int
    status: str = "pending" # pending, completed
    metadata: Dict[str, Any] = {}

class MathTodayTasksResponse(BaseModel):
    tasks: List[MathTask]
    summary: str
