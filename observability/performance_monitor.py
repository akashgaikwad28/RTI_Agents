"""
observability/performance_monitor.py
-------------------------------------
Background tasks and utilities to monitor event loop lag, memory usage, CPU usage.
"""

import asyncio
import time
import os
import psutil
from observability.metrics import (
    rti_memory_usage_mb, 
    rti_cpu_usage_percent, 
    rti_event_loop_lag
)
from observability.logger import get_logger

logger = get_logger("performance_monitor")

async def monitor_event_loop_lag(interval: float = 1.0):
    """
    Background task to monitor asyncio event loop lag.
    If the event loop is blocked, this task will wake up late.
    """
    while True:
        start_time = time.monotonic()
        await asyncio.sleep(interval)
        end_time = time.monotonic()
        
        lag = (end_time - start_time) - interval
        if lag > 0.05:  # Log if lag is greater than 50ms
            logger.warning(
                "Event loop blocked!", 
                extra={"event": "event_loop_blocked", "component": "api", "operation": "monitoring", "lag_seconds": lag}
            )
        
        rti_event_loop_lag.set(lag)

async def monitor_system_metrics(interval: float = 5.0):
    """
    Background task to monitor RAM and CPU of the current process.
    """
    process = psutil.Process(os.getpid())
    while True:
        try:
            mem_info = process.memory_info()
            cpu_percent = process.cpu_percent(interval=None) # Non-blocking read
            
            rti_memory_usage_mb.set(mem_info.rss / (1024 * 1024))
            rti_cpu_usage_percent.set(cpu_percent)
            
        except Exception as e:
            logger.error(
                f"Failed to collect system metrics: {e}",
                extra={"event": "system_metric_error", "component": "api", "operation": "monitoring"}
            )
            
        await asyncio.sleep(interval)

async def start_performance_monitors():
    """Starts all performance background tasks."""
    asyncio.create_task(monitor_event_loop_lag())
    asyncio.create_task(monitor_system_metrics())
    logger.info(
        "Performance monitors started.",
        extra={"event": "performance_monitors_started", "component": "api", "operation": "startup"}
    )
