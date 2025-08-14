"""
Utility functions for FastAPI lifespan management.
"""
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Callable, Awaitable
from fastapi import FastAPI

from app.core.context import get_bound_logger


class LifespanManager:
    """
    Manager for handling application lifespan with multiple resources.
    """
    
    def __init__(self):
        self.startup_tasks: List[Callable[[], Awaitable[None]]] = []
        self.shutdown_tasks: List[Callable[[], Awaitable[None]]] = []
        self.state: Dict[str, Any] = {}
        self.logger = get_bound_logger("app.lifespan")
    
    def add_startup_task(self, task: Callable[[], Awaitable[None]], name: str = None):
        """Add a startup task."""
        if name:
            task._task_name = name
        self.startup_tasks.append(task)
    
    def add_shutdown_task(self, task: Callable[[], Awaitable[None]], name: str = None):
        """Add a shutdown task."""
        if name:
            task._task_name = name
        self.shutdown_tasks.append(task)
    
    def startup(self, name: str = None):
        """Decorator to register startup tasks."""
        def decorator(func: Callable[[], Awaitable[None]]):
            self.add_startup_task(func, name or func.__name__)
            return func
        return decorator
    
    def shutdown(self, name: str = None):
        """Decorator to register shutdown tasks."""
        def decorator(func: Callable[[], Awaitable[None]]):
            self.add_shutdown_task(func, name or func.__name__)
            return func
        return decorator
    
    async def run_startup_tasks(self):
        """Run all startup tasks."""
        self.logger.info("Running startup tasks", total_tasks=len(self.startup_tasks))
        
        for i, task in enumerate(self.startup_tasks, 1):
            task_name = getattr(task, '_task_name', f'task_{i}')
            
            try:
                self.logger.info("Starting task", task_name=task_name, task_number=i)
                await task()
                self.logger.info("Task completed", task_name=task_name)
                
            except Exception as e:
                self.logger.error(
                    "Startup task failed",
                    task_name=task_name,
                    error=str(e),
                    error_type=type(e).__name__,
                    exc_info=True
                )
                raise
        
        self.logger.info("All startup tasks completed successfully")
    
    async def run_shutdown_tasks(self):
        """Run all shutdown tasks in reverse order."""
        self.logger.info("Running shutdown tasks", total_tasks=len(self.shutdown_tasks))
        
        # Run shutdown tasks in reverse order
        for i, task in enumerate(reversed(self.shutdown_tasks), 1):
            task_name = getattr(task, '_task_name', f'task_{len(self.shutdown_tasks) - i + 1}')
            
            try:
                self.logger.info("Starting shutdown task", task_name=task_name, task_number=i)
                await task()
                self.logger.info("Shutdown task completed", task_name=task_name)
                
            except Exception as e:
                self.logger.error(
                    "Shutdown task failed",
                    task_name=task_name,
                    error=str(e),
                    error_type=type(e).__name__,
                    exc_info=True
                )
                # Continue with other shutdown tasks even if one fails
        
        self.logger.info("All shutdown tasks completed")
    
    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """Create lifespan context manager."""
        try:
            await self.run_startup_tasks()
            yield
        finally:
            await self.run_shutdown_tasks()


# Global lifespan manager instance
lifespan_manager = LifespanManager()


# Convenience decorators using global manager
def startup(name: str = None):
    """Decorator to register startup tasks with global manager."""
    return lifespan_manager.startup(name)


def shutdown(name: str = None):
    """Decorator to register shutdown tasks with global manager."""
    return lifespan_manager.shutdown(name)


# Common resource management functions
async def setup_database_connection():
    """Example database setup function."""
    logger = get_bound_logger("app.database")
    logger.info("Setting up database connection")
    
    # Simulate database setup
    await asyncio.sleep(0.1)
    
    # Store connection info in lifespan state
    lifespan_manager.state["database"] = {
        "status": "connected",
        "pool_size": 10,
        "host": "localhost",
        "port": 5432
    }
    
    logger.info("Database connection established", 
               pool_size=lifespan_manager.state["database"]["pool_size"])


async def setup_redis_cache():
    """Example Redis cache setup function."""
    logger = get_bound_logger("app.cache")
    logger.info("Setting up Redis cache")
    
    # Simulate Redis setup
    await asyncio.sleep(0.05)
    
    lifespan_manager.state["redis"] = {
        "status": "connected",
        "host": "localhost",
        "port": 6379,
        "max_memory": "256MB"
    }
    
    logger.info("Redis cache connected", 
               host=lifespan_manager.state["redis"]["host"])


async def setup_background_tasks():
    """Example background tasks setup."""
    logger = get_bound_logger("app.background")
    logger.info("Starting background tasks")
    
    # Simulate background task setup
    await asyncio.sleep(0.02)
    
    lifespan_manager.state["background_tasks"] = {
        "status": "running",
        "tasks": ["cleanup_task", "metrics_task", "health_check_task"]
    }
    
    logger.info("Background tasks started", 
               task_count=len(lifespan_manager.state["background_tasks"]["tasks"]))


async def cleanup_database_connection():
    """Example database cleanup function."""
    logger = get_bound_logger("app.database")
    logger.info("Closing database connections")
    
    if "database" in lifespan_manager.state:
        # Simulate cleanup
        await asyncio.sleep(0.05)
        del lifespan_manager.state["database"]
        logger.info("Database connections closed")


async def cleanup_redis_cache():
    """Example Redis cache cleanup function."""
    logger = get_bound_logger("app.cache")
    logger.info("Closing Redis connections")
    
    if "redis" in lifespan_manager.state:
        # Simulate cleanup
        await asyncio.sleep(0.02)
        del lifespan_manager.state["redis"]
        logger.info("Redis connections closed")


async def cleanup_background_tasks():
    """Example background tasks cleanup function."""
    logger = get_bound_logger("app.background")
    logger.info("Stopping background tasks")
    
    if "background_tasks" in lifespan_manager.state:
        # Simulate cleanup
        await asyncio.sleep(0.03)
        del lifespan_manager.state["background_tasks"]
        logger.info("Background tasks stopped")


# Pre-configured lifespan managers for common scenarios
def create_database_lifespan_manager():
    """Create a lifespan manager focused on database resources."""
    manager = LifespanManager()
    manager.add_startup_task(setup_database_connection, "database_setup")
    manager.add_shutdown_task(cleanup_database_connection, "database_cleanup")
    return manager


def create_full_stack_lifespan_manager():
    """Create a lifespan manager for full-stack applications."""
    manager = LifespanManager()
    
    # Startup tasks (order matters)
    manager.add_startup_task(setup_database_connection, "database_setup")
    manager.add_startup_task(setup_redis_cache, "redis_setup")
    manager.add_startup_task(setup_background_tasks, "background_tasks_setup")
    
    # Shutdown tasks (will run in reverse order)
    manager.add_shutdown_task(cleanup_background_tasks, "background_tasks_cleanup")
    manager.add_shutdown_task(cleanup_redis_cache, "redis_cleanup")
    manager.add_shutdown_task(cleanup_database_connection, "database_cleanup")
    
    return manager


# Health check function that uses lifespan state
def get_application_health():
    """Get application health based on lifespan state."""
    if not lifespan_manager.state:
        return {
            "status": "starting",
            "message": "Application is starting up",
            "resources": {}
        }
    
    healthy_resources = {}
    unhealthy_resources = {}
    
    for resource_name, resource_info in lifespan_manager.state.items():
        if isinstance(resource_info, dict):
            status = resource_info.get("status", "unknown")
            if status in ["connected", "running", "ready"]:
                healthy_resources[resource_name] = resource_info
            else:
                unhealthy_resources[resource_name] = resource_info
        else:
            unhealthy_resources[resource_name] = {"status": "unknown", "info": resource_info}
    
    overall_status = "healthy" if not unhealthy_resources else "degraded"
    if not healthy_resources and unhealthy_resources:
        overall_status = "unhealthy"
    
    return {
        "status": overall_status,
        "healthy_resources": healthy_resources,
        "unhealthy_resources": unhealthy_resources,
        "total_resources": len(lifespan_manager.state)
    }
