from apps.planner.views import (
    DaySettingsViewSet,
    PostalCodeRangePresetViewSet,
    TeamSettingsViewSet,
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"team-settings", TeamSettingsViewSet, basename="team-settings")
router.register(r"day-settings", DaySettingsViewSet, basename="day-settings")
router.register(
    r"postal-code-ranges-presets",
    PostalCodeRangePresetViewSet,
    basename="postal-code-ranges-presets",
)
