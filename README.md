# Server Monitor ChatGPT Action



FastAPI-сервис для мониторинга Linux-сервера с интеграцией в ChatGPT через OpenAPI Actions.
Проект позволяет получать статистику сервера прямо из ChatGPT: CPU, RAM, диск, сеть, uptime, топ процессов и статус Docker-контейнеров.



## Возможности

- Мониторинг CPU
- Мониторинг RAM и swap
- Проверка свободного места на диске
- Сетевая статистика
- Uptime сервера
- Топ процессов
- Статус Docker-контейнеров
- Защита API через токен в header
- Интеграция с ChatGPT через OpenAPI Action
- Запуск через Docker Compose
- Работа через Caddy и HTTPS

## Как это работает

Общая схема:

```text
Custom GPT
   ↓
GPT Action
   ↓
HTTPS API endpoint
   ↓
Caddy reverse proxy
   ↓
FastAPI container
   ↓
Telegram Bot API
   ↓
Получение ответа о статистики сервера
```

Пользователь пишет в Custom GPT, например:

```text
Покажи мне информацию о состоянии моего сервера Х
```

GPT Action вызывает endpoint `/server/full`, сервис проверяет токен, форматирует ответ и отправляет обратно в GPT Action.

---

## Стек

- Python
- FastAPI
- psutil
- Docker SDK for Python
- Docker
- Caddy
- OpenAPI
- ChatGPT Actions
- Linux

## Переменные окружения 

SERVER_MONITOR_TOKEN=change_me_to_long_random_token: этот токен используется для защиты API.
Клиент должен передавать его в header x-monitor-token.

## Endpoints

GET /health - нужен токен, возвращает информацию о сервере, слежит для получения информации о самом сервере 

По умолчанию приложение запускается на порту 8010 `curl -H "x-monitor-token: your_token_here" http://localhost:8010/health` 

Replace your_token_here with the value of SERVER_MONITOR_TOKEN from your .env file.

Ответ:
```json
{
    "status": "ok",
    "service": "server-monitor-api"
}
```

GET /server/stats - нужен токен, возвращает информацию о статистике сервера, реализается для проверки активности сервера

По умолчанию приложение запускается на порту 8010 `curl -H "x-monitor-token: your_token_here" http://localhost:8010/server/stats` 

Replace your_token_here with the value of SERVER_MONITOR_TOKEN from your .env file.

Ответ:
```json
{
    "server_time": "2026-06-13T07:43:16.761893+00:00",
    "uptime": {
        "boot_time": "2026-05-22T14:08:00+00:00",
        "uptime_seconds": 1877716,
        "human": "21d 17h 35m"
    },
    "cpu": {
        "percent": 4.1,
        "cores_logical": 1,
        "cores_physical": 1,
        "load_average": [
            0.0927734375,
            0.02392578125,
            0.00537109375
        ]
    },
    "memory": {
        "ram": {
            "total_gb": 1.92,
            "used_gb": 0.37,
            "available_gb": 1.36,
            "percent": 29.2
        },
        "swap": {
            "total_gb": 0.0,
            "used_gb": 0.0,
            "percent": 0.0
        }
    },
    "disk": {
        "path": "/",
        "total_gb": 49.12,
        "used_gb": 5.1,
        "free_gb": 41.96,
        "percent": 10.8
    },
    "network": {
        "total_sent_mb": 921.96,
        "total_received_mb": 3186.76,
        "sent_per_sec_mb": 0.0,
        "received_per_sec_mb": 0.0
    },
    "summary": {
        "status": "ok",
        "warnings": []
    }
}
```

GET /server/docker - нужен токен, возвращает всю информацию о докерах, запущенных на сервере, реализовывает функционал инфрмационности о докерах 

По умолчанию приложение запускается на порту 8010 `curl -H "x-monitor-token: your_token_here" http://localhost:8010/server/docker` 

Replace your_token_here with the value of SERVER_MONITOR_TOKEN from your .env file.

Ответ:
```json
{
    "available": true,
    "containers": [
        {
            "name": "server-monitor",
            "status": "running",
            "image": "server-monitor-chatgpt-action-server-monitor:latest"
        },
        {
            "name": "amnezia-awg2",
            "status": "running",
            "image": "amnezia-awg2:latest"
        },
        {
            "name": "fitness-backend",
            "status": "running",
            "image": "fitness-connector-fitness-backend:latest"
        },
        {
            "name": "chatgpt-devlog-telegram-bridge",
            "status": "running",
            "image": "chatgpt-devlog-telegram-bridge-chatgpt-devlog-telegram-bridge:latest"
        },
        {
            "name": "caddy",
            "status": "running",
            "image": "caddy:2-alpine"
        }
    ]
}
```

GET /server/full - нужен токен, возвращает всю информацию о сервере, реализовывает функционал инфрмационности о сервере 

По умолчанию приложение запускается на порту 8010 `curl -H "x-monitor-token: your_token_here" http://localhost:8010/server/full` 

Replace your_token_here with the value of SERVER_MONITOR_TOKEN from your .env file.

Ответ:
```json
{
    "server_time": "2026-06-13T07:03:59.114747+00:00",
    "uptime": {
        "boot_time": "2026-05-22T14:08:00+00:00",
        "uptime_seconds": 1875358,
        "human": "21d 16h 55m"
    },
    "cpu": {
        "percent": 5.1,
        "cores_logical": 1,
        "cores_physical": 1,
        "load_average": [
            0.07861328125,
            0.1318359375,
            0.05224609375
        ]
    },
    "memory": {
        "ram": {
            "total_gb": 1.92,
            "used_gb": 0.39,
            "available_gb": 1.34,
            "percent": 30.1
        },
        "swap": {
            "total_gb": 0.0,
            "used_gb": 0.0,
            "percent": 0.0
        }
    },
    "disk": {
        "path": "/",
        "total_gb": 49.12,
        "used_gb": 5.1,
        "free_gb": 41.96,
        "percent": 10.8
    },
    "network": {
        "total_sent_mb": 921.49,
        "total_received_mb": 3185.04,
        "sent_per_sec_mb": 0.0,
        "received_per_sec_mb": 0.0
    },
    "docker": {
        "available": true,
        "containers": [
            {
                "name": "server-monitor",
                "status": "running",
                "image": "server-monitor-chatgpt-action-server-monitor:latest"
            }
        ]
    },
    "top_processes": [
        {
            "pid": 777,
            "name": "dockerd",
            "cpu_percent": 0,
            "memory_percent": 6.44
        }
    ],
    "summary": {
        "status": "ok",
        "warnings": []
    }
}
```

## Структура проекта


```text

server-monitor-chatgpt-action/

├── app/

│   └── main.py

├── Dockerfile

├── docker-compose.yml

├── requirements.txt

├── openapi-actions.yaml

├── .env.example

├── .gitignore

└── README.md

