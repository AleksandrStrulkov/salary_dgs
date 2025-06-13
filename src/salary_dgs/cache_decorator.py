def cache_result(method):
    """Универсальный декоратор кеша для методов расчета"""
    async def wrapper(self, *args, **kwargs):
        key = method.__name__
        if key in self._cache:
            return self._cache[key]
        result = await method(self, *args, **kwargs)
        self._cache[key] = result
        return result
    return wrapper
