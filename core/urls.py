from rest_framework import routers
from .views import CustomUserViewSet, PostViewSet, Chat

router = routers.SimpleRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'posts', PostViewSet)
router.register(r'chat', Chat)

urlpatterns = router.urls