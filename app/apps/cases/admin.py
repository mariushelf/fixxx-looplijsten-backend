from apps.cases.models import Case, Project, Stadium, StadiumLabel
from django.contrib import admin


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ("case_id", "is_top_bwv_case")
    search_fields = ("case_id",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Stadium)
class StadiumAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(StadiumLabel)
class StadiumLabelAdmin(admin.ModelAdmin):
    list_display = ("stadium", "label")
