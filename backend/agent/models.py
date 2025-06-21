# models.py

# User profile schema
from datetime import datetime
from typing import Literal
from typing import Optional

from langgraph.graph import MessagesState
from pydantic import BaseModel, Field


class Profile(BaseModel):
    """memory中存储user的schema。以profile形式"""
    name: Optional[str] = Field(description="The user's name", default=None)
    location: Optional[str] = Field(description="The user's location", default=None)
    job: Optional[str] = Field(description="The user's job", default=None)
    connections: list[str] = Field(
        description="Personal connection of the user, such as family members, friends, or coworkers",
        default_factory=list
    )
    interests: list[str] = Field(
        description="Interests that the user has",
        default_factory=list
    )


# To Do schema
class ToDo(BaseModel):
    task: str = Field(description="The task to be completed.")
    time_to_complete: Optional[int] = Field(description="Estimated time to complete the task (minutes).")
    deadline: Optional[datetime] = Field(
        description="When the task needs to be completed by (if applicable)",
        default=None
    )
    solutions: list[str] = Field(
        description="List of specific, actionable solutions (e.g., specific ideas, service providers, or concrete options relevant to completing the task)",
        min_items=1,
        default_factory=list
    )
    status: Literal["not started", "in progress", "done", "archived"] = Field(
        description="Current status of the task",
        default="not started"
    )
    planned_edits: Optional[list[str]] = Field(
        description="Planned changes or improvements to the task, such as adding specific vendors or clarifying vague goals.",
        default_factory=list
    )

class Instruction(BaseModel):
    language: str = Field(description="The language of the user, for task storage and reply")
    content: str = Field(description="The instruction text")


class CustomState(MessagesState, total=False):
    """继承自 MessagesState，增加 search_results 用于保存网络搜索结果。"""
    search_results: Optional[str]