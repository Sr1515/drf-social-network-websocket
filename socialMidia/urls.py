
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.urls import urlpatterns as urlpatter

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(urlpatter)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
