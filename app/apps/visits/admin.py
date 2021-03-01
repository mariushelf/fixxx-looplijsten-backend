from apps.visits.models import (
    Observation,
    Situation,
    SuggestNextVisit,
    Visit,
    VisitMetaData,
)
from django.contrib import admin


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ("author", "start_time", "case_id")


@admin.register(VisitMetaData)
class VisitMetaData(admin.ModelAdmin):
    list_display = ("visit", "date", "case_id")

    def date(self, obj):
        return obj.visit.start_time

    def case_id(self, obj):
        return obj.visit.itinerary_item

    # def has_change_permission(self, request, obj=None):
    #     return False

    # def has_delete_permission(self, request, obj=None):
    #     return False

    # def has_add_permission(self, request):
    #     return False


@admin.register(Situation)
@admin.register(Observation)
@admin.register(SuggestNextVisit)
class ChoiceItemAdmin(admin.ModelAdmin):
    list_display = ("value", "position", "verbose")
    list_editable = ("position",)
    ordering = ("position",)
