from apps.cases.views import CaseSearchViewSet, CaseViewSet, PermitViewSet
from apps.fraudprediction import router as fraudprediction_router
from apps.fraudprediction.views import FraudPredictionScoringViewSet
from apps.health.views import health_bwv, health_default
from apps.itinerary import router as itinerary_router
from apps.itinerary import router_v2 as itinerary_router_v2
from apps.itinerary.views import (
    ItineraryItemViewSet,
    ItineraryViewSet,
    ItineraryViewSetV2,
    NoteViewSet,
)
from apps.permits.views import DecosAPISearch, DecosViewSet
from apps.planner.views import (
    DaySettingsViewSet,
    PostalCodeRangePresetViewSet,
    TeamSettingsViewSet,
)
from apps.planner.views import dumpdata as planner_dumpdata
from apps.planner.views_sandbox import AlgorithmListView, AlgorithmView, BWVTablesView
from apps.users.views import IsAuthorizedView, ObtainAuthTokenOIDC, UserListView
from apps.visits.views import ObservationViewSet, SuggestNextVisitViewSet, VisitViewSet
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view

schema_view = get_schema_view(title="Example API")

admin.site.site_header = "Wonen looplijsten"
admin.site.site_title = "Wonen looplijsten"
admin.site.index_title = "Wonen looplijsten"

# v1 router
# api_router = DefaultRouter()
# api_router.register(r"itineraries", ItineraryViewSet, basename="itinerary")
# api_router.register(r"itinerary-items", ItineraryItemViewSet, basename="itinerary-item")
# api_router.register(r"cases", CaseViewSet, basename="case")
# api_router.register(r"search", CaseSearchViewSet, basename="search")
# api_router.register(r"notes", NoteViewSet, basename="notes")
# api_router.register(r"permits", PermitViewSet, basename="permits")
# api_router.register(r"decos", DecosViewSet, basename="decos")
# api_router.register(r"users", UserListView, basename="users")
# api_router.register(r"visits", VisitViewSet, basename="visits")
# api_router.register(r"observations", ObservationViewSet, basename="observations")
# api_router.register(
#     r"suggest-next-visit", SuggestNextVisitViewSet, basename="suggest-next-visit"
# )

# api_router.register(r"team-settings", TeamSettingsViewSet, basename="team-settings")
# api_router.register(r"day-settings", DaySettingsViewSet, basename="day-settings")
# api_router.register(
#     r"postal-code-ranges-presets",
#     PostalCodeRangePresetViewSet,
#     basename="postal-code-ranges-presets",
# )
# api_router.register(
#     r"fraud-prediction/scoring",
#     FraudPredictionScoringViewSet,
#     basename="fraud-prediction-score",
# )

# v2 router
# api_router_v2 = DefaultRouter()
# api_router_v2.register(r"itineraries", ItineraryViewSetV2, basename="itinerary")
# api_router_v2.register(r"itinerary-items", ItineraryItemViewSet, basename="itinerary-item")
# api_router_v2.register(r"cases", CaseViewSet, basename="case")
# api_router_v2.register(r"search", CaseSearchViewSet, basename="search")
# api_router_v2.register(r"notes", NoteViewSet, basename="notes")
# api_router_v2.register(r"permits", PermitViewSet, basename="permits")
# api_router_v2.register(r"decos", DecosViewSet, basename="decos")
# api_router_v2.register(r"users", UserListView, basename="users")
# api_router_v2.register(r"visits", VisitViewSet, basename="visits")
# api_router_v2.register(r"observations", ObservationViewSet, basename="observations")
# api_router_v2.register(
#     r"suggest-next-visit", SuggestNextVisitViewSet, basename="suggest-next-visit"
# )

# api_router_v2.register(r"team-settings", TeamSettingsViewSet, basename="team-settings")
# api_router_v2.register(r"day-settings", DaySettingsViewSet, basename="day-settings")
# api_router_v2.register(
#     r"postal-code-ranges-presets",
#     PostalCodeRangePresetViewSet,
#     basename="postal-code-ranges-presets",
# )
# api_router_v2.register(
#     r"fraud-prediction/scoring",
#     FraudPredictionScoringViewSet,
#     basename="fraud-prediction-score",
# )


urlpatterns = [
    # Admin environment
    path("admin/", admin.site.urls),
    path("admin/planner/dumpdata", planner_dumpdata, name="planner-dumpdata"),
    # Algorithm sandbox environment
    path("admin/bwv-structure", BWVTablesView.as_view(), name="bwv-structure"),
    path("algorithm/", AlgorithmListView.as_view(), name="algorithm-list"),
    path("algorithm/<int:pk>", AlgorithmView.as_view(), name="algorithm-detail"),
    # Health check urls
    path("looplijsten/health", health_default, name="health-default"),
    path("looplijsten/health_bwv", health_bwv, name="health-bwv"),
    path("health/", include("health_check.urls")),
    # The API for requesting data
    path(
        "api/v1/",
        include((itinerary_router.api_router, "itineraries"), namespace="v1"),
        name="api",
    ),
    # path("api/v1/", include((fraudprediction_router.api_router, "fraudprediction"), namespace="v1"), name="api_v2"),
    path(
        "api/v2/",
        include((itinerary_router_v2.api_router, "itineraries"), namespace="v2"),
        name="api_v2",
    ),
    # Authentication endpoint for exchanging an OIDC code for a token
    path(
        "api/v1/oidc-authenticate/",
        ObtainAuthTokenOIDC.as_view(),
        name="oidc-authenticate",
    ),
    # Endpoint for checking if user is authenticated
    path(
        "api/v1/is-authorized/",
        IsAuthorizedView.as_view(),
        name="is-authorized",
    ),
    path(
        "api/v2/is-authorized/",
        IsAuthorizedView.as_view(),
        name="is-authorized",
    ),
    # # Swagger/OpenAPI documentation
    path("api/v1/schema/", SpectacularAPIView.as_view(api_version="v1"), name="schema"),
    path(
        "api/v1/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/v2/schema/", SpectacularAPIView.as_view(api_version="v2"), name="schema_v2"
    ),
    path(
        "api/v2/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema_v2"),
        name="swagger-ui",
    ),
    path("admin/decos-api-search/", DecosAPISearch.as_view(), name="decos_api_search"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# JSON handlers for errors
handler500 = "rest_framework.exceptions.server_error"
handler400 = "rest_framework.exceptions.bad_request"
