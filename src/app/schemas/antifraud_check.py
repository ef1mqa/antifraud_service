from datetime import date
from typing import List
from pydantic import BaseModel, field_validator


class LoanHistoryItem(BaseModel):
    amount: int
    loan_data: date
    is_closed: bool

    @field_validator("loan_data", mode="before")
    @classmethod
    def parse_loan_data(cls, v: str) -> date:
        # ожидаем формат "DD.MM.YYYY"
        try:
            day, month, year = map(int, v.split("."))
            return date(year, month, day)
        except Exception as e:
            raise ValueError("Invalid date format, expected DD.MM.YYYY") from e


class UserCheck(BaseModel):
    birth_date: date
    phone_number: str
    loans_history: List[LoanHistoryItem]

    @field_validator("birth_date", mode="before")
    @classmethod
    def parse_birth_date(cls, v: str) -> date:
        try:
            day, month, year = map(int, v.split("."))
            return date(year, month, day)
        except Exception as e:
            raise ValueError("Invalid date format, expected DD.MM.YYYY") from e
        
class AntifroudRepsonse(BaseModel):
    client_check_status: bool
    failed_checks: list