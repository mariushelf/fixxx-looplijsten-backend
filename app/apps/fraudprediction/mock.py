def fraud_prediction_results():
    return {
        "prediction_woonfraude": {
            "3309": True,
            "3314": True,
            "3318": False,
        },
        "prob_woonfraude": {
            "3309": 0,
            "3314": 0.2,
            "3318": 0.61,
        },
        "business_rules": {
            "3309": {
                "begin_month": 0.034,
                "oppervlakte": 15,
            },
            "3314": {
                "begin_month": -0.021,
                "oppervlakte": 30,
            },
            "3318": {
                "begin_month": 0.178,
                "oppervlakte": 39,
            },
        },
        "shap_values": {
            "3309": {
                "begin_month": 0.034,
                "oppervlakte": -1.1,
            },
            "3314": {
                "begin_month": 0.034,
                "oppervlakte": -1.1,
            },
            "3318": {
                "begin_month": 0.034,
                "oppervlakte": -1.1,
            },
        },
        "feature_values": {
            "3309": {},
            "3314": {},
            "3318": {},
        },
    }
