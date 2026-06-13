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

## Примеры запросов

**Пример запроса:**
```text
Покажи мне информацию о состоянии моего сервера
```

**Пример ответа:**

```text
Состояние сервера нормальное, критичных проблем нет.

Основные показатели

CPU: 8.0%
Load average: 0.01 / 0.02 / 0.00
RAM: 0.38 / 1.92 GB, занято 29.4%
Swap: отсутствует, используется 0%
Диск /: 5.1 / 49.12 GB, занято 10.8%, свободно 41.96 GB
Сеть: сейчас 0 MB/s входящий и исходящий трафик
Uptime: 21 день 18 часов 22 минуты

Docker-контейнеры

server-monitor — running

Топ процессов

dockerd — CPU 0.1%, RAM 5.79%
systemd-journald — CPU 0%, RAM 5.76%

Вывод: всё выглядит штатно. Нагрузка низкая, RAM и диск используются умеренно, все Docker-контейнеры запущены.
```
**Пример запроса:**

```text
Покажи мне информацию в Docker контейнерах на сервере
```

**Пример ответа:**

```text
Docker на сервере доступен. Сейчас запущены 1 контейнер в статусе running.

Контейнер server-monitor
Статус running
Образ server-monitor:latest

Вывод: с Docker-контейнерами всё нормально — упавших или остановленных контейнеров не видно.
```

**Пример запроса:**

```text
Проверь жив ли сервер
```

**Пример ответа:**

```text
Да, сервер жив.

Server Monitor API отвечает: ok
Сервис мониторинга: server-monitor-api работает.
```

---

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

```env
SERVER_MONITOR_TOKEN=change_me_to_long_random_token: этот токен используется для защиты API.
```
Клиент должен передавать его в header x-monitor-token.

## Endpoints

> По умолчанию приложение запускается на порту 8010
> 
> Replace your_token_here with the value of SERVER_MONITOR_TOKEN from your .env file.

`GET /health` нужен токен, возвращает информацию о сервере, слежит для получения информации о самом сервере 

```bash
curl -H "x-monitor-token: your_token_here" http://localhost:8010/health
``` 

Пример ответа:
```json
{
    "status": "ok",
    "service": "server-monitor-api"
}
```

`GET /server/stats` нужен токен, возвращает информацию о статистике сервера, реализается для проверки активности сервера

```bash
curl -H "x-monitor-token: your_token_here" http://localhost:8010/server/stats 
```

Пример ответа:
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

`GET /server/docker` нужен токен, возвращает всю информацию о докерах, запущенных на сервере, реализовывает функционал инфрмационности о докерах 

```bash
curl -H "x-monitor-token: your_token_here" http://localhost:8010/server/docker 
```

Пример ответа:
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

`GET /server/full` нужен токен, возвращает всю информацию о сервере, реализовывает функционал инфрмационности о сервере 

```bash
curl -H "x-monitor-token: your_token_here" http://localhost:8010/server/full
```

Пример ответа:
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

## Запуск через Docker Compose

1. Зайдите в папку с проектом

2. Проверьте наличие файлов командой 
```bash
ls -la
```

Вы должны увилеить список файлов:
```docker-compose.yml
Dockerfile
.env
app/
requirements.txt
```

4. Затем запускаем Docker Compose командой 
```bash
 docker compose up -d --build
```

6. Проверка запуска командой 
```bash
docker compose ps
```

В ответ должны увидеть `server-monitor running`

8. Проверить логи 
```bash
docker compose logs --tail=100
```
В ответ должны увидеть `Uvicorn running on http://0.0.0.0:8010`

9. Проверяем API curl 
```bash
http://localhost:8010/health
```

В ответ должны увидеть
```json
{
  "status": "ok",
  "service": "server-monitor-api"
}
```

9. Для остановки проекта
```bash
docker compose down
```

10. Для перезапуска проекта
```bash
docker compose restart
```

Или что бы полностью пересоздать
```bash
docker compose down
docker compose up -d --build
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
```

## Планы дальнейшего развития

1. Реализовать возность настроить уведомления на определённую дату, время или частоту
2. Разработать возможность получить информачию через telegramm API
3. Реализовать получение информации о сервере за конкретный промежуток времени
4. Реализовать возможность на перезагружать сервер в критические моменты в ручную
5. Реализовать возможность на сервере о перезапуске сервера и получение уведомелние причину и время
