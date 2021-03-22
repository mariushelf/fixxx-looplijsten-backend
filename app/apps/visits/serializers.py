from apps.cases.models import Case
from apps.users.serializers import UserSerializer
from apps.visits.models import (
    Observation,
    Situation,
    SuggestNextVisit,
    Visit,
    VisitTeamMember,
)
from rest_framework import serializers


class SituationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Situation
        fields = [
            "value",
            "verbose",
        ]


class SuggestNextVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuggestNextVisit
        fields = [
            "value",
            "verbose",
        ]


class ObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Observation
        fields = [
            "value",
            "verbose",
        ]


class VisitTeamMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = VisitTeamMember
        fields = (
            "id",
            "user",
        )


class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = ("id", "case_id")


class CaseField(serializers.RelatedField):
    def get_queryset(self):
        return Case.objects.all()

    def to_internal_value(self, data):
        print(data)
        return self.get_queryset().get(case_id=data)

    def to_representation(self, value):
        return CaseSerializer(value).data


class VisitSerializer(serializers.ModelSerializer):
    team_members = VisitTeamMemberSerializer(many=True, read_only=True)
    case_id = CaseField()

    class Meta:
        model = Visit
        fields = "__all__"


class ToZakenVisitSerializer(serializers.Serializer):
    case_identification = serializers.CharField()
    start_time = serializers.CharField()
    observations = serializers.ListField(child=serializers.CharField(max_length=255))
    situation = serializers.CharField()
    authors = serializers.ListField(child=serializers.CharField(max_length=255))
    can_next_visit_go_ahead = serializers.BooleanField(allow_null=True)
    can_next_visit_go_ahead_description = serializers.CharField(allow_null=True)
    suggest_next_visit = serializers.CharField(allow_null=True)
    suggest_next_visit_description = serializers.CharField(allow_null=True)
    notes = serializers.CharField(allow_null=True)
