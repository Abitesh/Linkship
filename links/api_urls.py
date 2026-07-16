from rest_framework.routers import DefaultRouter

from .views import URLViewSet

router = DefaultRouter()
router.register(r'urls', URLViewSet, basename='url')

urlpatterns = router.urls