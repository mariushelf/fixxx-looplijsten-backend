def get_team_schedules():
    return {
        "actions": [{"id": 1, "name": "Huisbezoek"}],
        "week_segments": [
            {"id": 1, "name": "Doordeweek"},
            {"id": 2, "name": "Weekend"},
        ],
        "day_segments": [{"id": 2, "name": "Avond"}, {"id": 1, "name": "Overdag"}],
        "priorities": [
            {"id": 1, "name": "Hoog", "weight": 1.0},
            {"id": 2, "name": "Normaal", "weight": 0.0},
        ],
    }
