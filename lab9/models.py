"""Схемы входа/выхода API (валидация выполняется здесь, на HTTP-границе)."""
from typing import Optional

from pydantic import BaseModel, Field

CODE_PATTERN = r"^[A-Z]{2,10}[0-9]{2,4}$"


class CourseCreate(BaseModel):
    code: str = Field(..., pattern=CODE_PATTERN, examples=["NOSQL301"])
    title: str = Field(..., min_length=3, max_length=120)
    teacher: str = Field(..., min_length=2, max_length=80)
    room: str = Field(..., min_length=1, max_length=20, examples=["A-204"])
    credits: int = Field(3, ge=1, le=10)


class RoomUpdate(BaseModel):
    room: str = Field(..., min_length=1, max_length=20)


class CourseOut(BaseModel):
    code: str
    title: str
    teacher: str
    room: str
    credits: int


class ErrorOut(BaseModel):
    detail: str
