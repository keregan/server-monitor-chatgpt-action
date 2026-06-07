import os
import time
from datetime import datetime, timezone

import docker
import psutil
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException


load_dotenv()

app = FastAPI(
    title="Server Monitor API",
    description="Simple API for checking server CPU, RAM, disk, network and Docker containers.",
    version="1.0.0",
)

SERVER_MONITOR_TOKEN = os.getenv("SERVER_MONITOR_TOKEN")


def check_token(x_monitor_token: str | None):
    if not SERVER_MONITOR_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="SERVER_MONITOR_TOKEN is not configured",
        )

    if x_monitor_token != SERVER_MONITOR_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Invalid monitor token",
        )


def bytes_to_gb(value: int) -> float:
    return round(value / 1024 / 1024 / 1024, 2)


def bytes_to_mb(value: int) -> float:
    return round(value / 1024 / 1024, 2)


def get_uptime() -> dict:
    boot_time = psutil.boot_time()
    uptime_seconds = int(time.time() - boot_time)

    days = uptime_seconds // 86400
    hours = (uptime_seconds % 86400) // 3600
    minutes = (uptime_seconds % 3600) // 60

    return {
        "boot_time": datetime.fromtimestamp(boot_time, timezone.utc).isoformat(),
        "uptime_seconds": uptime_seconds,
        "human": f"{days}d {hours}h {minutes}m",
    }


def get_cpu() -> dict:
    return {
        "percent": psutil.cpu_percent(interval=1),
        "cores_logical": psutil.cpu_count(logical=True),
        "cores_physical": psutil.cpu_count(logical=False),
        "load_average": os.getloadavg() if hasattr(os, "getloadavg") else None,
    }


def get_memory() -> dict:
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()

    return {
        "ram": {
            "total_gb": bytes_to_gb(memory.total),
            "used_gb": bytes_to_gb(memory.used),
            "available_gb": bytes_to_gb(memory.available),
            "percent": memory.percent,
        },
        "swap": {
            "total_gb": bytes_to_gb(swap.total),
            "used_gb": bytes_to_gb(swap.used),
            "percent": swap.percent,
        },
    }


def get_disk() -> dict:
    disk = psutil.disk_usage("/")

    return {
        "path": "/",
        "total_gb": bytes_to_gb(disk.total),
        "used_gb": bytes_to_gb(disk.used),
        "free_gb": bytes_to_gb(disk.free),
        "percent": disk.percent,
    }


def get_network() -> dict:
    first = psutil.net_io_counters()
    time.sleep(1)
    second = psutil.net_io_counters()

    sent_per_sec = second.bytes_sent - first.bytes_sent
    recv_per_sec = second.bytes_recv - first.bytes_recv

    return {
        "total_sent_mb": bytes_to_mb(second.bytes_sent),
        "total_received_mb": bytes_to_mb(second.bytes_recv),
        "sent_per_sec_mb": bytes_to_mb(sent_per_sec),
        "received_per_sec_mb": bytes_to_mb(recv_per_sec),
    }


def get_top_processes(limit: int = 5) -> list[dict]:
    processes = []

    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            info = proc.info
            processes.append(
                {
                    "pid": info.get("pid"),
                    "name": info.get("name"),
                    "cpu_percent": info.get("cpu_percent") or 0,
                    "memory_percent": round(info.get("memory_percent") or 0, 2),
                }
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    processes.sort(
        key=lambda item: item["cpu_percent"] + item["memory_percent"],
        reverse=True,
    )

    return processes[:limit]


def get_docker_containers() -> dict:
    try:
        client = docker.from_env()
        containers = client.containers.list(all=True)

        result = []

        for container in containers:
            result.append(
                {
                    "name": container.name,
                    "status": container.status,
                    "image": container.image.tags[0] if container.image.tags else "unknown",
                }
            )

        return {
            "available": True,
            "containers": result,
        }

    except Exception as error:
        return {
            "available": False,
            "error": str(error),
            "containers": [],
        }


def get_summary(cpu: dict, memory: dict, disk: dict) -> dict:
    warnings = []

    if cpu["percent"] >= 85:
        warnings.append("High CPU usage")

    if memory["ram"]["percent"] >= 85:
        warnings.append("High RAM usage")

    if disk["percent"] >= 80:
        warnings.append("Disk usage is high")

    status = "ok" if not warnings else "warning"

    return {
        "status": status,
        "warnings": warnings,
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "server-monitor-api",
    }


@app.get("/server/stats")
def server_stats(x_monitor_token: str | None = Header(default=None)):
    check_token(x_monitor_token)

    cpu = get_cpu()
    memory = get_memory()
    disk = get_disk()
    network = get_network()
    uptime = get_uptime()

    return {
        "server_time": datetime.now(timezone.utc).isoformat(),
        "uptime": uptime,
        "cpu": cpu,
        "memory": memory,
        "disk": disk,
        "network": network,
        "summary": get_summary(cpu, memory, disk),
    }


@app.get("/server/docker")
def server_docker(x_monitor_token: str | None = Header(default=None)):
    check_token(x_monitor_token)

    return get_docker_containers()


@app.get("/server/full")
def server_full(x_monitor_token: str | None = Header(default=None)):
    check_token(x_monitor_token)

    cpu = get_cpu()
    memory = get_memory()
    disk = get_disk()
    network = get_network()
    uptime = get_uptime()
    docker_info = get_docker_containers()
    top_processes = get_top_processes()

    return {
        "server_time": datetime.now(timezone.utc).isoformat(),
        "uptime": uptime,
        "cpu": cpu,
        "memory": memory,
        "disk": disk,
        "network": network,
        "docker": docker_info,
        "top_processes": top_processes,
        "summary": get_summary(cpu, memory, disk),
    }
