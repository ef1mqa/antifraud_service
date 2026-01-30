from fastapi import APIRouter, Body
from app.schemas import UserCheck, AntifroudRepsonse
from app.services.checks import check_user

router = APIRouter(
    prefix="/antifroud_service",
    tags=["system"],
)

@router.post("/check", response_model=AntifroudRepsonse)
async def antifroud_checking(
    data: UserCheck = Body(
        example={
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
    )
) -> AntifroudRepsonse:
    result = check_user(data)
    return AntifroudRepsonse(**result)



