from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from collections import defaultdict
from exams.models import Exam, ExamAttempt, Question
from monitoring.models import Screenshot, Violation
from django_ratelimit.decorators import ratelimit
from django.shortcuts import get_object_or_404
from core.permissions import IsOrgAdmin, IsOrgInvigilator
from datetime import timedelta
from django.utils.timezone import now
from django.utils.dateparse import parse_datetime
from exams.serializers import ExamSerializer, ExamDetailSerializer
from django.contrib.auth import get_user_model
from exams.models import QuestionOption


User = get_user_model()


# ---------------- LIVE MONITOR ----------------

@api_view(['GET'])
@permission_classes([IsOrgInvigilator])
def live_monitor(request, exam_id):

    org = request.user.current_organisation

    exam = get_object_or_404(Exam, id=exam_id, organisation=org)

    data = []

    attempts = (
        ExamAttempt.objects
        .filter(exam=exam)
        .select_related("user")
        .order_by("user_id", "-start_time", "-id")
    )

    seen_users = set()
    current_time = now()
    HEARTBEAT_THRESHOLD = timedelta(seconds=60)

    for attempt in attempts:
        if attempt.user_id in seen_users:
            continue
        seen_users.add(attempt.user_id)

        is_online = (current_time - attempt.last_active) < HEARTBEAT_THRESHOLD

        display_status = "active" if (attempt.status == 'active' and is_online) else "inactive"
        if attempt.status == 'terminated':
            display_status = 'terminated'

        latest_violation = (
            Violation.objects
            .filter(attempt=attempt)
            .order_by("-timestamp")
            .first()
        )

        metadata = latest_violation.metadata if latest_violation and latest_violation.metadata else {}

        latest_screenshot = (
            Screenshot.objects
            .filter(attempt=attempt)
            .order_by("-timestamp")
            .first()
        )

        system_health = {
            "camera": metadata.get("camera", True),
            "tab_focus": metadata.get("tab", True),
            "fullscreen": metadata.get("fullscreen", True)
        }

        data.append({
            "username": attempt.user.username,
            "attempt_id": attempt.id,
            "violations_count": attempt.total_violations,
            "risk_score": attempt.risk_score,
            "status": display_status,
            "system_health": system_health,

            "latest_violation": {
                "type": latest_violation.violation_type,
                "severity": latest_violation.severity,
                "timestamp": latest_violation.timestamp
            } if latest_violation else None,

            "latest_screenshot": {
                "id": latest_screenshot.id,
                "image_url": latest_screenshot.image if latest_screenshot else None,  # ✅ FIXED
                "timestamp": latest_screenshot.timestamp
            } if latest_screenshot else None
        })

    return Response(data)


# ---------------- USER DETAIL ----------------

@api_view(['GET'])
@permission_classes([IsOrgInvigilator])
def user_detail(request, username):
    return _user_detail_response(request, username=username)


@api_view(['GET'])
@permission_classes([IsOrgInvigilator])
def user_detail_exam(request, exam_id, username):
    return _user_detail_response(request, username=username, exam_id=exam_id)


def _user_detail_response(request, username, exam_id=None):

    org = request.user.current_organisation

    violations = Violation.objects.filter(
        attempt__user__username=username,
        attempt__exam__organisation=org
    )

    if exam_id:
        violations = violations.filter(attempt__exam_id=exam_id)

    breakdown = {}
    for v in violations:
        breakdown[v.violation_type] = breakdown.get(v.violation_type, 0) + 1

    screenshots = Screenshot.objects.filter(
        attempt__user__username=username,
        attempt__exam__organisation=org
    )

    if exam_id:
        screenshots = screenshots.filter(attempt__exam_id=exam_id)

    screenshots = screenshots.order_by("-timestamp")[:10]

    screenshot_items = [
        {
            "id": s.id,
            "image_url": s.image,  # ✅ FIXED
            "timestamp": s.timestamp,
            "violation_type": None,
            "ml_face_detected": None,
            "ml_multiple_faces": None
        }
        for s in screenshots
    ]

    return Response({
        "breakdown": breakdown,
        "screenshots": screenshot_items,
        "images": [s.image for s in screenshots]
    })


# ---------------- CLEAR VIOLATIONS ----------------

@ratelimit(key='user', rate='5/m', method='POST', block=True)
@api_view(['DELETE', 'POST'])
@permission_classes([IsOrgAdmin])
def clear_violations(request, username):

    org = request.user.current_organisation

    Violation.objects.filter(
        attempt__user__username=username,
        attempt__exam__organisation=org
    ).delete()

    return Response({"status": "cleared"})


@api_view(['DELETE', 'POST'])
@permission_classes([IsOrgAdmin])
def clear_violations_exam(request, exam_id, username):

    org = request.user.current_organisation

    Violation.objects.filter(
        attempt__user__username=username,
        attempt__exam_id=exam_id,
        attempt__exam__organisation=org
    ).delete()

    return Response({"status": "cleared"})


# ---------------- EXAMS ----------------

@api_view(['GET'])
@permission_classes([IsOrgAdmin])
def list_exams(request):

    org = request.user.current_organisation

    exams = Exam.objects.filter(organisation=org)

    serializer = ExamDetailSerializer(exams, many=True)
    return Response(serializer.data)


@ratelimit(key='user', rate='5/m', method='POST', block=True)
@api_view(['POST'])
@permission_classes([IsOrgAdmin])
def toggle_exam(request, exam_id):

    org = request.user.current_organisation

    exam = get_object_or_404(Exam, id=exam_id, organisation=org)

    exam.is_active = not exam.is_active
    exam.save()

    if not exam.is_active:
        ExamAttempt.objects.filter(
            exam=exam,
            status="active"
        ).update(status="terminated")

    return Response({"status": "toggled"})


@api_view(['GET'])
@permission_classes([IsOrgAdmin])
def list_all_users(request):

    org = request.user.current_organisation

    users = User.objects.filter(
        memberships__organisation=org
    ).values('id', 'username', 'first_name', 'last_name')

    return Response(list(users))


# ---------------- UPDATE EXAM ----------------

@ratelimit(key='user', rate='3/m', method='PATCH', block=True)
@api_view(['PATCH'])
@permission_classes([IsOrgAdmin])
def update_exam(request, exam_id):

    org = request.user.current_organisation

    exam = get_object_or_404(Exam, id=exam_id, organisation=org)

    exam.title = request.data.get("title", exam.title)
    exam.description = request.data.get("description", exam.description)
    exam.duration = request.data.get("duration", exam.duration)

    start_time_input = request.data.get("start_time")
    end_time_input = request.data.get("end_time")

    if start_time_input:
        start_time = parse_datetime(start_time_input)
        if not start_time:
            return Response({"error": "Invalid start_time"}, status=400)
        exam.start_time = start_time

    if end_time_input:
        end_time = parse_datetime(end_time_input)
        if not end_time:
            return Response({"error": "Invalid end_time"}, status=400)
        exam.end_time = end_time

    exam.save()

    exam.questions.all().delete()

    for q in request.data.get("questions", []):
        options_data = q.get("options") or []

        question = Question.objects.create(
            exam=exam,
            text=q.get("text"),
            question_type=q.get("question_type", "mcq"),
            points=q.get("points", 1),
            negative_points=q.get("negative_points", 0),
            order=q.get("order", 0),
            image=q.get("image"),
            correct_text_answer=q.get("correct_text_answer"),
            explanation=q.get("explanation"),
        )

        for opt in options_data:
            QuestionOption.objects.create(
                question=question,
                text=opt.get("text"),
                is_correct=opt.get("is_correct", False)
            )

    return Response({"status": "updated"})

# ---------------- CREATE / DELETE ----------------

@ratelimit(key='user', rate='2/m', method='POST', block=True)
@api_view(['POST'])
@permission_classes([IsOrgAdmin])
def create_exam(request):

    serializer = ExamSerializer(data=request.data, context={"request":request})

    if serializer.is_valid():
        exam = serializer.save(
            created_by=request.user,
            organisation=request.user.current_organisation
        )

        return Response({
            "status": "created",
            "exam_id": exam.id
        })

    return Response(serializer.errors, status=400)


@ratelimit(key='user', rate='2/m', method='DELETE', block=True)
@api_view(['DELETE'])
@permission_classes([IsOrgAdmin])
def delete_exam(request, exam_id):

    org = request.user.current_organisation

    exam = get_object_or_404(Exam, id=exam_id, organisation=org)
    exam.delete()

    return Response({"status": "deleted"})


# ---------------- QA + RESULTS ----------------

@api_view(['GET'])
@permission_classes([IsOrgAdmin])
def exam_qa(request, exam_id):

    org = request.user.current_organisation

    questions = Question.objects.filter(
        exam_id=exam_id,
        exam__organisation=org
    )

    data = []
    for q in questions:
        data.append({
            "id": q.id,
            "text": q.text,
            "question_type": q.question_type,
            "points": q.points,
            "options": [
                {
                    "id": opt.id,
                    "text": opt.text,
                    "is_correct": opt.is_correct
                }
                for opt in q.options.all()
             ],
            "correct_text_answer": q.correct_text_answer
    })

    return Response(data)


@api_view(['GET'])
@permission_classes([IsOrgAdmin])
def exam_results(request, exam_id):

    org = request.user.current_organisation

    attempts = ExamAttempt.objects.filter(
        exam_id=exam_id,
        exam__organisation=org
    ).select_related('user')

    user_data = defaultdict(list)

    for a in attempts:
        user_data[a.user.username].append(a)

    data = []

    for username, attempts_list in user_data.items():
        latest = attempts_list[-1]

        data.append({
        "username": username,
        "attempts": len(attempts_list),
        "points_scored": latest.points_scored,
        "total_points": latest.total_points,
        "start_time": latest.start_time,
        "end_time": latest.end_time,
         })
    return Response(data)