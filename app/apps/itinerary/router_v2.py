from apps.itinerary.views import ItineraryViewSetV2
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"itineraries", ItineraryViewSetV2, basename="itinerary")

api_router = router.urls
