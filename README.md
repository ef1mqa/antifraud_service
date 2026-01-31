# Сервис антифрода

Сервис реализует проверку базовых антифрод‑правил для клиента перед кредитным скорингом.

## Легенда

Сервис принимает набор данных клиента, полученных из сторонней системы (хранилища данных), и на основе этих данных выполняет проверки правил, которые могут остановить дальнейший кредитный скоринг.

## Функциональность и требования

Сервис реализует один основной эндпоинт:

`POST /antifroud_service/check`

### Входные данные

Тело запроса — объект с полями:

- `birth_date` — дата рождения в формате `DD.MM.YYYY`.
- `phone_number` — номер телефона клиента.
- `loans_history` — список займов, каждый элемент содержит:
  - `amount` — сумма займа;
  - `loan_data` — дата оформления займа в формате `DD.MM.YYYY`;
  - `is_closed` — флаг закрытия займа (`true` / `false`).

### Логика работы эндпоинта

1. Перед выполнением проверок сервис строит ключ для Redis по входным данным и проверяет, есть ли в Redis закэшированный результат проверки.
2. Если результат в Redis **есть**:
   - сервис возвращает его из кэша без повторного выполнения бизнес‑логики.
3. Если результата в Redis **нет**:
   - сервис выполняет последовательность проверок:
     - если телефон **не** начинается с `+7` или `8` — срабатывает стоп‑фактор;
     - если клиенту **меньше 18 лет** — срабатывает стоп‑фактор;
     - если у клиента есть **хотя бы один незакрытый займ** (`is_closed == false`) — срабатывает стоп‑фактор;
   - формируется список не пройденных проверок и итоговый флаг прохождения/непрохождения.
   - полученный результат кэшируется в Redis с ограниченным временем жизни (TTL).

### Ответ эндпоинта

Ответ содержит:

- итоговый флаг прохождения/непрохождения проверок;
- список сработавших проверок (стоп‑факторов).

## Технологии

- FastAPI + Pydantic — веб‑фреймворк и валидация входных данных.
- Redis — кэширование результатов проверок.
- Pytest — тесты сервиса.
- Prometheus — сбор метрик сервиса (эндпоинт `/metrics`).
- Grafana — визуализация метрик Prometheus.
- Docker / docker-compose — контейнеризация сервиса, Redis, Prometheus и Grafana.

## Запуск

### Локальный запуск (через uv)

Требуется установленный `uv`.

```bash
# Установка зависимостей
uv sync

# Запуск сервиса локально
uv run src/run.py
```

После запуска:

- Swagger UI: http://localhost:8080/docs
- Эндпоинт проверки: POST http://localhost:8080/antifroud_service/check
- Метрики Prometheus: http://localhost:8080/metrics

> Для локального запуска без Docker Redis должен быть доступен по тому же хосту и порту, что и в конфигурации (`REDIS_HOST` и порт 6379).

### Запуск всего окружения через Docker

```bash
docker-compose up --build
```

После старта контейнеров:

- сервис антифрода: http://localhost:8080
- Swagger UI: http://localhost:8080/docs
- метрики сервиса: http://localhost:8080/metrics
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

## Примеры запросов

### Запрос, который проходит проверки

Тело запроса:

```json
{
  "birth_date": "30.01.1994",
  "phone_number": "+79876543210",
  "loans_history": [
    {
      "amount": 10000,
      "loan_data": "30.01.2010",
      "is_closed": true
    },
    {
      "amount": 15000,
      "loan_data": "28.02.2011",
      "is_closed": true
    }
  ]
}
```

Пример запроса из bash:

```bash
curl -X POST "http://localhost:8080/antifroud_service/check" \
  -H "Content-Type: application/json" \
  -d '{"birth_date":"30.01.1994","phone_number":"+79876543210","loans_history":[{"amount":10000,"loan_data":"30.01.2010","is_closed":true},{"amount":15000,"loan_data":"28.02.2011","is_closed":true}]}' \
  -w '\n time_total: %{time_total}s\n'
```

### Запрос, который не проходит проверки

Тело запроса:

```json
{
  "birth_date": "30.01.2009",
  "phone_number": "79876543210",
  "loans_history": [
    {
      "amount": 10000,
      "loan_data": "30.01.2010",
      "is_closed": true
    },
    {
      "amount": 15000,
      "loan_data": "28.02.2011",
      "is_closed": false
    }
  ]
}
```

Пример запроса из bash:

```bash
curl -X POST "http://localhost:8080/antifroud_service/check" \
  -H "Content-Type: application/json" \
  -d '{"birth_date":"30.01.2009","phone_number":"79876543210","loans_history":[{"amount":10000,"loan_data":"30.01.2010","is_closed":true},{"amount":15000,"loan_data":"28.02.2011","is_closed":false}]}' \
  -w '\n time_total: %{time_total}s\n'
```

Такие же тела можно использовать в Swagger UI (http://localhost:8080/docs), выбрав эндпоинт POST /antifroud_service/check и подставив JSON в поле Request body.

## Метрики и дашборд Grafana

Сервис экспонирует Prometheus‑метрики по адресу `/metrics`.

Ключевые метрики:

- `http_requests_total` — количество запросов с лейблами `handler`, `method`, `status`.
- `http_request_duration_seconds` — гистограмма времени ответа с разбивкой по `handler` и `method`.

В Grafana можно собрать дашборд:

- панель 1 — количество запросов по статусам:

  ```promql
  sum by (status) (http_requests_total)
  ```

- панель 2 — 95‑й перцентиль времени ответа по хендлерам/методам:

  ```promql
  histogram_quantile(
    0.95,
    sum by (le, handler, method) (
      rate(http_request_duration_seconds_bucket[1m])
    )
  )
  ```