# organisations/plan_features.py

PLAN_FEATURES = {
    "free": {
        "allowed_question_types": ["mcq"],
        "max_questions": 10,
        "image_questions": False,
        "file_upload": False,
    },
    "pro": {
        "allowed_question_types": ["mcq", "true_false", "short_answer"],
        "max_questions": 50,
        "image_questions": True,
        "file_upload": False,
    },
    "enterprise": {
        "allowed_question_types": ["mcq", "true_false", "short_answer", "image_based", "file_upload"],
        "max_questions": 200,
        "image_questions": True,
        "file_upload": True,
    }
}


def get_plan_features(org):
    return PLAN_FEATURES.get(org.plan, PLAN_FEATURES["free"])