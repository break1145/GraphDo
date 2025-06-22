# models.py

import json
from datetime import datetime
from typing import Any, Literal, Optional

from langgraph.graph import MessagesState
from pydantic import BaseModel, Field


class Profile(BaseModel):
    """用户信息的持久化记忆存储。以profile形式"""
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

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Profile":
        interests = data.get("interests")
        if isinstance(interests, str):
            try:
                data["interests"] = json.loads(interests)
            except json.JSONDecodeError:
                data["interests"] = []
        connections = data.get("connections")
        if isinstance(connections, str):
            try:
                data["connections"] = json.loads(connections)
            except json.JSONDecodeError:
                data["connections"] = []
        return cls.model_validate(data)


class ToDo(BaseModel):
    """to do 事项的结构化存储。collection形式"""
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
    key: str = Field(description="The uuid of the task.")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ToDo":
        if "solutions" in data and isinstance(data["solutions"], str):
            try:
                data["solutions"] = json.loads(data["solutions"])
            except json.JSONDecodeError:
                data["solutions"] = []

        if "planned_edits" in data and isinstance(data["planned_edits"], str):
            try:
                data["planned_edits"] = json.loads(data["planned_edits"])
            except json.JSONDecodeError:
                data["planned_edits"] = []

        if "deadline" in data and isinstance(data["deadline"], str):
            try:
                data["deadline"] = datetime.fromisoformat(data["deadline"])
            except ValueError:
                data["deadline"] = None

        return cls.model_validate(data)

class Instruction(BaseModel):
    """用户偏好的结构化存储。以collection形式"""
    language: str = Field(description="The language of the user, for task storage and reply")
    content: str = Field(description="The instruction text")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Instruction":
        return cls.parse_obj(data)

class CustomState(MessagesState, total=False):
    """继承自 MessagesState，增加 search_results 用于保存网络搜索结果。"""
    search_results: Optional[str]