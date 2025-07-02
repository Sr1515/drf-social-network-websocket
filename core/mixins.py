from django.core.cache import cache
from rest_framework.response import Response

class CacheMixin:
    cache_timeout = 60 * 60  

    def get_cache_key(self, request):
        region = getattr(self, 'cache_region', 'default')
        return f"{region}:cache{request.path}?{request.META.get('QUERY_STRING', '')}"

    def list(self, request, *args, **kwargs):
        cache_key = self.get_cache_key(request)
        cache_data = cache.get(cache_key)

        if cache_data:
            return Response(cache_data)
        
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        if isinstance(serializer.data, (dict, list)):
            cache.set(cache_key, serializer.data, timeout=self.cache_timeout)
        
        return Response(serializer.data)
    
    def invalidate_cache(self, request, *args, **kwargs):
        cache_key = self.get_cache_key(request)
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, timeout=self.cache_timeout)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        self.invalidate_cache(request, *args, **kwargs)
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        self.invalidate_cache(request, *args, **kwargs)
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        self.invalidate_cache(request, *args, **kwargs)
        return response
