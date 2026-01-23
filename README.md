Установка uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Установка версии Python
```bash
uv python install 3.12
```

Инициализация проекта
```bash
uv init --python 3.12
```


```bash
uv venv --python 3.12
```

Добавление библиотек
```bash
uv add 'uvicorn>=0.40.0'
uv add 'fastapi>=0.122.0'
uv add 'pydantic>=2.12.5'
uv add pydantic-settings
uv add pyyaml
uv add --dev 'pytest>=9.0.1'
```

Запуск
```bash
uv run src/run.py
```


Сборка в Docker
```bash
docker build -t service-template:latest .
```

Запуск в Docker
```bash
docker run -p 8080:8080 service-template:latest
```
