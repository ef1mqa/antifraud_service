import pytest


@pytest.mark.asyncio
async def test_antifraud_failed_checks(client):
    """
    Клиент: <18 лет, есть незакрытый займ, номер без +7/8.
    Ожидаем: client_check_status=False и соответствующие причины.
    """
    payload = {
        "birth_date": "30.01.2009",
        "phone_number": "79876543210",
        "loans_history": [
            {
                "amount": 10000,
                "loan_data": "30.01.2010",
                "is_closed": True,
            },
            {
                "amount": 15000,
                "loan_data": "28.02.2011",
                "is_closed": False,
            },
        ],
    }

    response = await client.post("/antifroud_service/check", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["client_check_status"] is False
    # порядок не так важен, проверяем по содержимому
    assert "Клиенту меньше 18 лет" in data["failed_checks"]
    assert (
        "Указанный номер телефона не соответствует требованию(начинается с +7 или 8)"
        in data["failed_checks"]
    )
    assert "У клиента есть не закрытый займ" in data["failed_checks"]


@pytest.mark.asyncio
async def test_antifraud_success_and_cache(client):
    """
    Клиент: >=18 лет, все займы закрыты, номер корректный.
    Проверяем, что:
    - первый запрос возвращает client_check_status=True
    - второй запрос с тем же payload тоже OK (по сути, из кэша)
    """
    payload = {
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

    # первый запрос
    resp1 = await client.post("/antifroud_service/check", json=payload)
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["client_check_status"] is True
    assert data1["failed_checks"] == []

    # второй запрос (должен использовать кэш, но для теста достаточно, что ответ тот же)
    resp2 = await client.post("/antifroud_service/check", json=payload)
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2 == data1
