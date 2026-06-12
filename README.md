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
GET /server/stats - нужен токен, возвращает информацию о статистике сервера, реализается для проверки активности сервера
GET /server/docker - нужен токен, возвращает всю информацию о докерах, запущенных на сервере, реализовывает функционал инфрмационности о докерах 
GET /server/full - нужен токен, возвращает всю информацию о сервере, реализовывает функционал инфрмационности о сервере 

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

