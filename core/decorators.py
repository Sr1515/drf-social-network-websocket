from functools import wraps
from django.core.cache import cache
from rest_framework.response import Response
import jsonpickle

def cache_action(func):
    @wraps(func)
    def wrapper(viewset, request, *args, **kwargs):
        cache_key = viewset.get_cache_key(request)
        cache_data = cache.get(cache_key)

        if cache_data:
            print(f'dados retornados do redis {cache_key}')
            return Response(jsonpickle.loads(cache_data))

        response = func(viewset, request, *args, **kwargs)

        if isinstance(response.data, (list, dict)):
            cache.set(cache_key, jsonpickle.dumps(response.data), timeout=viewset.cache_timeout)
        
        return response

    return wrapper