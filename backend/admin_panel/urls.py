from django.urls import path
from .views import *

urlpatterns = [
    path("exam/<int:exam_id>/live/", live_monitor),
    path("exam/<int:exam_id>/pdf/", export_pdf),
    path("exam/<int:exam_id>/excel/", export_excel),
    path("exam/<int:exam_id>/user/<str:username>/", user_detail_exam),
    path("exam/<int:exam_id>/user/<str:username>/clear/", clear_violations_exam),

    path("user/<str:username>/", user_detail),
    path("user/<str:username>/clear/", clear_violations),

    path("exam/create/", create_exam),
    path("exam/list/", list_exams),
    path("exam/<int:exam_id>/toggle/", toggle_exam),
    path('users/', list_all_users),
    path("exam/<int:exam_id>/update-time/", update_exam_time),
]
