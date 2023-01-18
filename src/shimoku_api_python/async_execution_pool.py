import asyncio
from functools import wraps

task_pool = []


def async_auto_call_manager(sequential: bool = False, execute: bool = False, task_pool=task_pool):
    def decorator(async_func):
        async def execute_tasks():
            await asyncio.gather(*task_pool)
            task_pool.clear()

        @wraps(async_func)
        def wrapper(*args, **kwargs):
            nonlocal task_pool
            if sequential:
                if len(task_pool) > 0:
                    asyncio.run(execute_tasks())
                return asyncio.run(async_func(*args, **kwargs))
            else:
                task_pool += [async_func(*args, **kwargs)]
                if execute:
                    asyncio.run(execute_tasks())

        return wrapper

    return decorator
