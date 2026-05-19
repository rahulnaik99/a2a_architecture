"""
A2A Protocol Models
"""

from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field
from uuid import uuid4
from datetime import datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class TaskState(str, Enum):
    SUBMITTED = "submitted"
    WORKING   = "working"
    COMPLETED = "completed"
    FAILED    = "failed"


class A2ATaskRequest(BaseModel):
    task_id:    str           = Field(default_factory=lambda: str(uuid4()))
    query:      str
    caller_id:  str           = "orchestrator"
    created_at: str           = Field(default_factory=_now)


class A2ATaskResponse(BaseModel):
    task_id:      str
    state:        TaskState
    result:       Any            = None
    error:        Optional[str]  = None      # ← was str, crashed on None
    created_at:   str            = Field(default_factory=_now)
    completed_at: Optional[str]  = None      # ← was str, crashed on None


class AgentSkill(BaseModel):
    name:        str
    description: str


class AgentCard(BaseModel):
    name:              str
    version:           str            = "1.0.0"
    description:       str
    url:               str
    a2a_task_endpoint: str            = "/a2a/task"
    health_endpoint:   str            = "/health"
    skills:            list[AgentSkill] = []
    supported_inputs:  list[str]      = []
    planner_hint:      str            = ""
    input_schema:      dict           = {}
    tags:              list[str]      = []
    supports_parallel: bool           = True
