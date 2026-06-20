# Server Monitor ChatGPT Action

FastAPI-сервис для мониторинга Linux-сервера с интеграцией в ChatGPT через OpenAPI Actions.

Проект позволяет получать информацию о состоянии сервера прямо из ChatGPT: CPU, RAM, swap, диск, сеть, uptime, топ процессов и статус Docker-контейнеров.

## Возможности

- Мониторинг CPU
- Мониторинг RAM и swap
- Проверка свободного места на диске
- Сетевая статистика
- Uptime сервера
- Топ процессов
- Проверка статуса Docker-контейнеров
- Защита API через токен в header `x-monitor-token`
- Интеграция с ChatGPT через OpenAPI Action
- Запуск через Docker Compose
- Возможность работы через reverse proxy и HTTPS

## Примеры запросов в ChatGPT

### Запрос

```text
Покажи мне информацию о состоянии моего сервера
```

### Ответ

```text
Состояние сервера нормальное, критичных проблем нет.

Основные показатели:

CPU: 8.0%
Load average: 0.01 / 0.02 / 0.00
RAM: 0.38 / 1.92 GB, занято 29.4%
Swap: отсутствует
Диск /: 5.1 / 49.12 GB, занято 10.8%, свободно 41.96 GB
Сеть: сейчас 0 MB/s входящий и исходящий трафик
Uptime: 21 день 18 часов 22 минуты

Docker-контейнеры:

server-monitor — running

Топ процессов:

dockerd — CPU 0.1%, RAM 5.79%
systemd-journald — CPU 0%, RAM 5.76%

Вывод: всё выглядит штатно. Нагрузка низкая, RAM и диск используются умеренно, Docker-контейнеры работают.
```

### Запрос

```text
Покажи мне информацию о Docker-контейнерах на сервере
```

### Ответ

```text
Docker на сервере доступен. Сейчас запущен 1 контейнер в статусе running.

Контейнер server-monitor
Статус: running
Образ: server-monitor:latest

Вывод: с Docker-контейнерами всё нормально — упавших или остановленных контейнеров не видно.
```

### Запрос

```text
Проверь, жив ли сервер
```

### Ответ

```text
Да, сервер жив.

Server Monitor API отвечает: ok.
Сервис мониторинга server-monitor-api работает.
```

## Как это работает

Общая схема работы проекта:

```text
Custom GPT
   ↓
GPT Action
   ↓
HTTPS API endpoint
   ↓
Reverse proxy, например Caddy
   ↓
FastAPI container
   ↓
psutil / Docker SDK
   ↓
Linux server metrics
```

ChatGPT обращается к API через OpenAPI Action.  
FastAPI получает запрос, проверяет токен доступа, собирает системные метрики сервера и возвращает результат в JSON-формате.

## Стек технологий

- Python
- FastAPI
- psutil
- Docker SDK for Python
- Docker
- Docker Compose
- OpenAPI
- ChatGPT Actions
- Linux
- Caddy / reverse proxy

## Переменные окружения

Для работы проекта нужен файл `.env`.

Пример:

```env
SERVER_MONITOR_TOKEN=change_me_to_long_random_token
```

`SERVER_MONITOR_TOKEN` используется для защиты API.  
Клиент должен передавать его в header:

```text
x-monitor-token: your_token_here
```

В репозиторий должен попадать только `.env.example`.  
Реальный `.env` с токеном не должен публиковаться в GitHub.

## API endpoints

По умолчанию приложение запускается на порту `8010`.

Базовый адрес для локальной проверки на сервере:

```text
http://localhost:8010
```

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/health` | No | Проверяет, что API работает |
| GET | `/server/stats` | Yes | Возвращает основную статистику сервера |
| GET | `/server/docker` | Yes | Возвращает информацию о Docker-контейнерах |
| GET | `/server/full` | Yes | Возвращает полную информацию о сервере |

### GET `/health`

Проверяет, что API работает.

Токен не требуется.

```bash
curl http://localhost:8010/health
```

Пример ответа:

```json
{
  "status": "ok",
  "service": "server-monitor-api"
}
```

### GET `/server/stats`

Возвращает основную статистику сервера: uptime, CPU, RAM, swap, диск, сеть и summary.

Требуется header `x-monitor-token`.

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
    "load_average": [0.09, 0.02, 0.01]
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

### GET `/server/docker`

Возвращает информацию о Docker-контейнерах на сервере.

Требуется header `x-monitor-token`.

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
      "image": "server-monitor:latest"
    },
    {
      "name": "example-service",
      "status": "running",
      "image": "example-service:latest"
    }
  ]
}
```

### GET `/server/full`

Возвращает полную информацию о сервере: системные метрики, Docker-контейнеры, топ процессов и summary.

Требуется header `x-monitor-token`.

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
    "load_average": [0.08, 0.13, 0.05]
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
        "image": "server-monitor:latest"
      }
    ]
  },
  "top_processes": [
    {
      "pid": 777,
      "name": "dockerd",
      "cpu_percent": 0.0,
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

Примечание по OpenAPI Actions

В файле openapi-actions.yaml используется пример адреса: https://your-domain.com/monitor

Перед подключением OpenAPI-схемы к ChatGPT Actions этот адрес нужно заменить на реальный публичный HTTPS-адрес вашего API.

Это сделано специально, чтобы не публиковать настоящий домен или адрес сервера в открытом репозитории.



### 1. Перейти в папку проекта

```bash
cd /opt/server-monitor-chatgpt-action
```

### 2. Проверить наличие файлов

```bash
ls -la
```

В папке проекта должны быть:

```text
docker-compose.yml
Dockerfile
.env
app/
requirements.txt
```

### 3. Создать `.env`, если его ещё нет

```bash
cp .env.example .env
```

После этого нужно открыть `.env` и указать свой токен:

```bash
nano .env
```

Пример содержимого:

```env
SERVER_MONITOR_TOKEN=your_long_random_token
```

### 4. Запустить проект

```bash
docker compose up -d --build
```

### 5. Проверить статус контейнера

```bash
docker compose ps
```

Ожидаемый результат:

```text
server-monitor   running
```

### 6. Проверить логи

```bash
docker compose logs --tail=100
```

Ожидаемый фрагмент в логах:

```text
Uvicorn running on http://0.0.0.0:8010
```

### 7. Проверить health endpoint

```bash
curl http://localhost:8010/health
```

Ожидаемый ответ:

```json
{
  "status": "ok",
  "service": "server-monitor-api"
}
```

### 8. Проверить защищённый endpoint

```bash
TOKEN=$(docker compose exec -T server-monitor printenv SERVER_MONITOR_TOKEN | tr -d '\r')
curl -s -H "x-monitor-token: $TOKEN" http://localhost:8010/server/full | python3 -m json.tool
```

### 9. Остановить проект

```bash
docker compose down
```

### 10. Перезапустить проект

```bash
docker compose restart
```

### 11. Полностью пересоздать контейнер

```bash
docker compose down
docker compose up -d --build
```

## Структура проекта

```text
server-monitor-chatgpt-action/
├── app/
│   └── main.py - основной файл FastAPI-приложения, здесь находятся API-эндпоинты для получения информации о сервере
├── Dockerfile - настройки для работы Docker
├── docker-compose.yml - файл для запуска проекта через Docker Compose
├── requirements.txt
├── openapi-actions.yaml - OpenAPI-схема для подключения проекта к ChatGPT Actions
├── .env.example - пример файла с переменными окружения. В нём показывается, какие настройки нужны для запуска проекта
├── .gitignore - файлы, которые будет игнопироватся при отправке в github
└── README.md - основная документация проекта: описание, запуск, проверка и возможности.
```

## Безопасность

Для сбора системных метрик контейнер использует доступ к ресурсам хост-сервера, включая host network, host PID namespace и Docker socket в режиме read-only.

Это нужно для получения информации о сервере и Docker-контейнерах, но такую конфигурацию следует запускать только на доверенном сервере.

- Реальный `.env` не должен попадать в GitHub.
- Токен доступа должен храниться только в переменной окружения `SERVER_MONITOR_TOKEN`.
- Защищённые endpoints требуют header `x-monitor-token`.
- В README не следует публиковать реальные токены, приватные IP-адреса, домены и чувствительные данные инфраструктуры.
- Для публичного доступа рекомендуется использовать HTTPS через reverse proxy.

## Статус проекта

Проект находится в стадии MVP.

Реализовано:

- сбор системных метрик сервера;
- проверка Docker-контейнеров;
- защита API через токен;
- OpenAPI-схема для ChatGPT Actions;
- запуск через Docker Compose.

## Планы дальнейшего развития

1. Добавить настройку порогов CPU, RAM и диска через переменные окружения.
2. Реализовать статусы `ok`, `warning` и `critical`.
3. Добавить уведомления при превышении критических значений.
4. Добавить сохранение истории метрик за выбранный период времени.
5. Добавить ежедневные отчёты о состоянии сервера.
6. Улучшить структуру проекта: вынести security, services, routers и schemas в отдельные модули.
7. Добавить тесты для основных endpoints.
8. Добавить отдельный файл `docs/API_EXAMPLES.md` с расширенными примерами запросов и ответов.
9. Автоматический и полу автоматически перезапуск сервера при критических ошибках
