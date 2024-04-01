from rest_framework.routers import SimpleRouter

from service.views import RoomViewSet, BookingViewSet

app_name = 'booking'

router = SimpleRouter()
router.register(r'room', RoomViewSet)
router.register(r'booking', BookingViewSet)

urlpatterns = []

urlpatterns += router.urls
