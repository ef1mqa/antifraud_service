from datetime import date
from typing import List
from pydantic import BaseModel, field_validator, ConfigDict


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

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "birth_date": "30.01.1994",
                "phone_number": "+79876543210",
                "loans_history": [
                    {
                        "amount": 10000,
                        "loan_data": "30.01.2010",
                        "is_closed": True,
                    },
                    {
                        "amount": 15000,
                        "loan_data": "28.02.2011",
                        "is_closed": True,
                    },
                ],
            }
        }
    )

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