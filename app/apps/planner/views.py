import datetime
import json
import sys

from apps.itinerary.models import Itinerary
from apps.planner.models import DaySettings, PostalCodeRangeSet, TeamSettings
from apps.planner.serializers import (
    CaseReasonSerializer,
    CaseStateTypeSerializer,
    DaySettingsSerializer,
    NewDaySettingsSerializer,
    PlannerSettingsSerializer,
    PostalCodeRangePresetSerializer,
    TeamScheduleTypesSerializer,
    TeamSettingsSerializer,
)
from constance.backends.database.models import Constance
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.management import call_command
from django.http import Http404, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet
from settings.const import DAY_SETTING_IN_USE

from .mock import get_team_reasons, get_team_schedules, get_team_state_types


class PostalCodeRangePresetViewSet(ModelViewSet):
    """
    A view for listing PostalCodeRangeSets
    """

    serializer_class = PostalCodeRangePresetSerializer
    queryset = PostalCodeRangeSet.objects.all()


class TeamSettingsViewSet(ModelViewSet):
    """
    A view for listing/adding/updating/removing a TeamSettings
    """

    serializer_class = TeamSettingsSerializer
    queryset = TeamSettings.objects.all()

    @extend_schema(
        description="Gets the reasons associated with the requested team",
        responses={status.HTTP_200_OK: CaseReasonSerializer(many=True)},
    )
    @action(
        detail=True,
        url_path="reasons",
        methods=["get"],
    )
    def reasons(self, request, pk):
        team_settings = self.get_object()
        data = []

        if team_settings.use_zaken_backend:
            serializer = CaseReasonSerializer(
                team_settings.fetch_team_reasons(request.headers.get("Authorization")),
                many=True,
            )
            data = serializer.data

        return Response(data)

    @extend_schema(
        description="Gets the Scheduling Types associated with the given team",
        responses={status.HTTP_200_OK: TeamScheduleTypesSerializer()},
    )
    @action(
        detail=True,
        url_path="schedule-types",
        methods=["get"],
    )
    def schedule_types(self, request, pk):
        team_settings = self.get_object()
        data = {}

        if team_settings.use_zaken_backend:
            serializer = TeamScheduleTypesSerializer(
                team_settings.fetch_team_schedules(request.headers.get("Authorization"))
            )
            data = serializer.data

        return Response(data)

    @extend_schema(
        description="Gets the CaseStateTypes associated with the given team",
        responses={status.HTTP_200_OK: CaseStateTypeSerializer(many=True)},
    )
    @action(
        detail=True,
        url_path="state-types",
        methods=["get"],
    )
    def state_types(self, request, pk):
        team_settings = self.get_object()
        data = []

        if team_settings.use_zaken_backend:
            serializer = CaseStateTypeSerializer(
                team_settings.fetch_team_state_types(
                    request.headers.get("Authorization")
                ),
                many=True,
            )
            data = serializer.data

        return Response(data)


class DaySettingsViewSet(ModelViewSet):
    """
    A view for listing/adding/updating/removing a DaySettings
    """

    serializer_class = DaySettingsSerializer
    queryset = DaySettings.objects.all()

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if not Itinerary.objects.filter(
                settings__day_settings=instance,
                created_at=datetime.datetime.now().strftime("%Y-%m-%d"),
            ):
                self.perform_destroy(instance)
            else:
                raise ValidationError(DAY_SETTING_IN_USE, 404)
        except Http404:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return NewDaySettingsSerializer
        return DaySettingsSerializer


@user_passes_test(lambda u: u.is_superuser)
def dumpdata(request):
    sysout = sys.stdout
    fname = "%s-%s.json" % ("top-planner", datetime.datetime.now().strftime("%Y-%m-%d"))
    response = HttpResponse(content_type="application/json")
    response["Content-Disposition"] = "attachment; filename=%s" % fname

    sys.stdout = response
    call_command(
        "dumpdata",
        "planner",
        "visits.Situation",
        "visits.Observation",
        "visits.SuggestNextVisit",
        "cases.Project",
        "cases.Stadium",
        "cases.StadiumLabel",
        "--indent=4",
    )
    sys.stdout = sysout

    return response
