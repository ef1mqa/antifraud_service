from datetime import date
from app.schemas import UserCheck

def is_18_or_older(birth_date: date) -> bool:
    today = date.today()
    eighteenth = birth_date.replace(year=birth_date.year+18)
    return today >= eighteenth

def check_phone_number(phone_number: str) -> bool:
    if phone_number[:2] == "+7" or phone_number[:1] == "8":
        return True
    return False

def check_loans(loans: list) -> bool:
    for loan in loans:
        if loan.is_closed == False:
            return False
    return True


def check_user(user: UserCheck) -> dict:
    reason_dont_check = {
         "check_age": "Клиенту меньше 18 лет",
         "phone_check": "Указанный номер телефона не соответствует требованию(начинается с +7 или 8)",
         "loan_check": "У клиента есть не закрытый займ"
    }
    failed_checks = []

    if not check_phone_number(user.phone_number):
        failed_checks.append(reason_dont_check["phone_check"])

    if not is_18_or_older(user.birth_date):
        failed_checks.append(reason_dont_check["check_age"])

    if not check_loans(user.loans_history):
        failed_checks.append(reason_dont_check["loan_check"])

    client_check_status = len(failed_checks) == 0

    return {
        "client_check_status": client_check_status,
        "failed_checks": failed_checks
    }