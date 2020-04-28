from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from api.itinerary.views import ItineraryViewSet, ItineraryItemViewSet, NoteViewSet
from api.cases.views import CaseViewSet, CaseSearchViewSet
from api.health.views import health_default, health_bwv
from api.users.views import ObtainAuthTokenOIDC, IsAuthenticatedView, UserListView
from api.planner.views_sandbox import AlgorithmView
from api.planner.views import ConstantsStadiaViewSet, ConstantsProjectsViewSet, SettingsPlannerViewSet
from api.fraudprediction.views import FraudPredictionScoringViewSet

admin.site.site_header = "Wonen looplijsten"
admin.site.site_title = "Wonen looplijsten"
admin.site.index_title = "Wonen looplijsten"

schema_view = get_schema_view(
    openapi.Info(title="Looplijsten API", default_version='v1'),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

api_router = DefaultRouter()
api_router.register(r'itineraries', ItineraryViewSet, basename='itinerary')
api_router.register(r'itinerary-items', ItineraryItemViewSet, basename='itinerary-item')
api_router.register(r'cases', CaseViewSet, basename='case')
api_router.register(r'search', CaseSearchViewSet, basename='search')
api_router.register(r'notes', NoteViewSet, basename='notes')
api_router.register(r'users', UserListView, basename='users')
api_router.register(r'constants/projects', ConstantsProjectsViewSet, basename='constants-projects')
api_router.register(r'constants/stadia', ConstantsStadiaViewSet, basename='constants-stadia')
api_router.register(r'settings/planner', SettingsPlannerViewSet, basename='settings-planner')
api_router.register(r'fraud-prediction/scoring', FraudPredictionScoringViewSet,
                    basename='fraud-prediction-score')

urlpatterns = [
    # Admin environment
    path('admin/', admin.site.urls),

    # Algorithm sandbox environment
    path('algorithm/', AlgorithmView.as_view(), name='algorithm'),

    # Health check urls
    path('looplijsten/health', health_default, name='health-default'),
    path('looplijsten/health_bwv', health_bwv, name='health-bwv'),

    # The API for requesting data
    path('api/v1/', include(api_router.urls)),

    # Authentication endpoint for exchanging an OIDC code for a token
    path('api/v1/oidc-authenticate/', ObtainAuthTokenOIDC.as_view(), name='oidc-authenticate'),

    # Endpoint for checking if user is authenticated
    path('api/v1/is-authenticated/', IsAuthenticatedView.as_view(), name='is-authenticated'),

    # Swagger/OpenAPI documentation
    path('api/v1/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# JSON handlers for errors
handler500 = 'rest_framework.exceptions.server_error'
handler400 = 'rest_framework.exceptions.bad_request'
