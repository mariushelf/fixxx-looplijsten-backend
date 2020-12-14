from types import SimpleNamespace

from apps.planner.algorithm.knapsack import ItineraryKnapsackList
from apps.planner.const import SCORING_WEIGHTS
from apps.planner.utils import remove_cases_from_list
from constance.backends.database.models import Constance
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from utils.queries_bwv import get_bwv_columns, get_bwv_tables

from .models import TeamSettings


class BWVTablesView(LoginRequiredMixin, TemplateView):
    template_name = "bwv_table.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tables = [
            {
                "name": t.get("table_name"),
                "columns": [
                    c.get("column_name") for c in get_bwv_columns(t.get("table_name"))
                ],
            }
            for t in get_bwv_tables()
        ]

        context.update(
            {
                "tables": tables,
            }
        )

        return context


class AlgorithmListView(LoginRequiredMixin, ListView):
    model = TeamSettings
    template_name = "team_settings_list.html"


class AlgorithmView(LoginRequiredMixin, DetailView):
    model = TeamSettings
    login_url = "/admin/login/"
    template_name = "body.html"

    def get_data(self, teamSettings):
        postal_codes = [{"range_start": 1000, "range_end": 1109}]
        weekday = "monday"
        day_part = "day"
        day_settings = (
            teamSettings.settings.get("days", {}).get(weekday, {}).get(day_part, {})
        )
        key, _ = Constance.objects.get_or_create(key=settings.CONSTANCE_MAPS_KEY)

        return {
            "projects": teamSettings.project_choices.all().values_list(
                "name", flat=True
            ),
            "selected_projects": teamSettings.settings.get("projects"),
            "stadia": teamSettings.stadia_choices.all().values_list("name", flat=True),
            "selected_stadia": day_settings.get("secondary_stadia"),
            "main_stadium": day_settings.get("primary_stadium"),
            "selected_exclude_stadia": day_settings.get("exclude_stadia"),
            "selected_opening_date": teamSettings.settings.get("opening_date"),
            "number_of_lists": 1,
            "length_of_list": teamSettings.settings.get("length_of_list", 8),
            "maps_key": key.value,
            "weight_distance": SCORING_WEIGHTS.DISTANCE.value,
            "weight_fraud_probability": SCORING_WEIGHTS.FRAUD_PROBABILITY.value,
            "weight_primary_stadium": SCORING_WEIGHTS.PRIMARY_STADIUM.value,
            "weight_secondary_stadium": SCORING_WEIGHTS.SECONDARY_STADIUM.value,
            "weight_issuemelding": SCORING_WEIGHTS.ISSUEMELDING.value,
            "start_case_id": "",
            "postal_code_range_start": teamSettings.settings.get(
                "postal_codes", postal_codes
            )[0].get("range_start"),
            "postal_code_range_end": teamSettings.settings.get(
                "postal_codes", postal_codes
            )[0].get("range_end"),
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data = self.get_data(self.object)

        context.update(data)

        my_settings = SettingsMock(data)
        generator = ItineraryKnapsackList(my_settings)
        unplanned_cases = generator.__get_eligible_cases__()

        context.update(
            {
                "planning": {
                    "planned_cases": [],
                    "unplanned_cases": unplanned_cases,
                }
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        opening_date = request.POST.get("opening_date")
        projects = request.POST.getlist("projects")
        length_of_list = int(request.POST.get("length_of_list"))
        stadia = request.POST.getlist("stadia")
        exclude_stadia = request.POST.getlist("exclude_stadia")
        main_stadium = request.POST.get("main_stadium")
        start_case_id = request.POST.get("start_case_id", "")

        weight_distance = float(request.POST.get("weight_distance"))
        weight_fraud_probability = float(request.POST.get("weight_fraud_probability"))
        weight_primary_stadium = float(request.POST.get("weight_primary_stadium"))
        weight_secondary_stadium = float(request.POST.get("weight_secondary_stadium"))
        weight_issuemelding = float(request.POST.get("weight_issuemelding"))

        postal_code_range_start = int(request.POST.get("postal_code_range_start"))
        postal_code_range_end = int(request.POST.get("postal_code_range_end"))

        context_data = self.get_data(self.get_object())
        context_data["selected_opening_date"] = opening_date
        context_data["selected_projects"] = projects
        context_data["length_of_list"] = length_of_list
        context_data["selected_stadia"] = stadia
        context_data["selected_exclude_stadia"] = exclude_stadia
        context_data["main_stadium"] = main_stadium
        context_data["weight_distance"] = weight_distance
        context_data["weight_fraud_probability"] = weight_fraud_probability
        context_data["weight_primary_stadium"] = weight_primary_stadium
        context_data["weight_secondary_stadium"] = weight_secondary_stadium
        context_data["weight_issuemelding"] = weight_issuemelding
        context_data["start_case_id"] = start_case_id
        context_data["postal_code_range_start"] = postal_code_range_start
        context_data["postal_code_range_end"] = postal_code_range_end
        context_data["postal_codes"] = [
            {
                "range_start": postal_code_range_start,
                "range_end": postal_code_range_end,
            },
        ]
        settings = SettingsMock(context_data)
        settings_weights = SettingsWeightMock(context_data)
        settings_postal_codes = SettingsPostalCodeMock(context_data)

        generator = ItineraryKnapsackList(
            settings=settings,
            settings_weights=settings_weights,
            postal_code_settings=settings_postal_codes.postal_codes.all(),
        )

        eligible_cases = generator.__get_eligible_cases__()
        planned_cases = generator.generate()
        unplanned_cases = remove_cases_from_list(eligible_cases, planned_cases)

        context_data["planning"] = {
            "planned_cases": planned_cases,
            "unplanned_cases": unplanned_cases,
        }

        return render(request, self.template_name, context_data)


class SettingsWeightMock(SimpleNamespace):
    """
    Creates a mock settings weight objects using context data. Should only be used for prototyping.
    """

    def __init__(self, context):
        super().__init__()
        self.distance = context["weight_distance"]
        self.fraud_probability = context["weight_fraud_probability"]
        self.primary_stadium = context["weight_primary_stadium"]
        self.secondary_stadium = context["weight_secondary_stadium"]
        self.issuemelding = context["weight_issuemelding"]


class SettingsPostalCodeMock(SimpleNamespace):
    """
    Creates a mock settings objects using context data. Should only be used for prototyping.
    """

    def __init__(self, context):
        super().__init__()
        self.postal_codes = SimpleNamespace()
        self.postal_codes.all = lambda: [
            SimpleNamespace(
                range_start=postal_codes.get("range_start"),
                range_end=postal_codes.get("range_end"),
            )
            for postal_codes in context["postal_codes"]
        ]


class SettingsMock(SimpleNamespace):
    """
    Creates a mock settings objects using context data. Should only be used for prototyping.
    """

    def __init__(self, context):
        super().__init__()
        self.opening_date = context["selected_opening_date"]
        self.target_length = context["length_of_list"]
        self.postal_code_range_start = context["postal_code_range_start"]
        self.postal_code_range_end = context["postal_code_range_end"]

        self.projects = SimpleNamespace()
        self.projects.all = lambda: [
            SimpleNamespace(name=project) for project in context["selected_projects"]
        ]

        if context.get("main_stadium", None):
            self.primary_stadium = SimpleNamespace(name=context["main_stadium"])

        self.secondary_stadia = SimpleNamespace()
        self.secondary_stadia.all = lambda: [
            SimpleNamespace(name=project) for project in context["selected_stadia"]
        ]

        self.exclude_stadia = SimpleNamespace()
        self.exclude_stadia.all = lambda: [
            SimpleNamespace(name=project)
            for project in context["selected_exclude_stadia"]
        ]

        self.start_case = SimpleNamespace()
        self.start_case.case_id = context["start_case_id"]
