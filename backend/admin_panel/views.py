from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from collections import defaultdict
from exams.models import Exam, ExamAttempt, Question
from monitoring.models import Screenshot, Violation


from reportlab.lib.styles import getSampleStyleSheet
from datetime import timedelta
from django.utils.timezone import now
from django.utils.dateparse import parse_datetime
from exams.serializers import ExamSerializer, ExamDetailSerializer


# live dashboard
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def live_monitor(request, exam_id):
    data = []
    # fetch all attemps
    attempts = (
        ExamAttempt.objects
        .filter(exam_id=exam_id)
        .select_related("user")
        .order_by("user_id", "-start_time", "-id")
    )

    seen_users = set()
    current_time = now()
    # threshold time to show
    HEARTBEAT_THRESHOLD = timedelta(seconds=60)

    for attempt in attempts:
        if attempt.user_id in seen_users:
            continue
        seen_users.add(attempt.user_id)

       
        # active vs inactive session
        is_online = (current_time - attempt.last_active) < HEARTBEAT_THRESHOLD
        
        # override the db status
        display_status = "active" if (attempt.status == 'active' and is_online) else "inactive"
        if attempt.status == 'terminated':
            display_status = 'terminated'

        #  latest vioaltion
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

        #  PAYLOAD
        data.append({
            "username": attempt.user.username,
            "attempt_id": attempt.id,
            "violations_count": attempt.total_violations,
            "risk_score": attempt.risk_score,
            "status": display_status, # 
            "system_health": system_health,

            # violation severity
            "latest_violation": {
                "type": latest_violation.violation_type,
                "severity": latest_violation.severity,
                "timestamp": latest_violation.timestamp
            } if latest_violation else None,
            
            "latest_screenshot": {
                "id": latest_screenshot.id,
                "image_url": f"data:image/png;base64,{latest_screenshot.image}" if latest_screenshot and latest_screenshot.image else None,
                "timestamp": latest_screenshot.timestamp
            } if latest_screenshot else None
        })

    return Response(data)


# user detail
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detail(request, username):

    return _user_detail_response(username=username)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detail_exam(request, exam_id, username):
    return _user_detail_response(username=username, exam_id=exam_id)


def _user_detail_response(username, exam_id=None):
    violations = Violation.objects.filter(
        attempt__user__username=username
    )
    if exam_id is not None:
        violations = violations.filter(attempt__exam_id=exam_id)

    breakdown = {}
    for v in violations:
        breakdown[v.violation_type] = breakdown.get(v.violation_type, 0) + 1

    screenshots = Screenshot.objects.filter(
        attempt__user__username=username
    )
    if exam_id is not None:
        screenshots = screenshots.filter(attempt__exam_id=exam_id)
    screenshots = screenshots.order_by("-timestamp")[:10]

    screenshot_items = [
        {
            "id": s.id,
            "image_url": s.image,
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


# clear violations
@api_view(['DELETE', 'POST'])
@permission_classes([IsAuthenticated])
def clear_violations(request, username):

    Violation.objects.filter(
        attempt__user__username=username
    ).delete()

    return Response({"status": "cleared"})


@api_view(['DELETE', 'POST'])
@permission_classes([IsAuthenticated])
def clear_violations_exam(request, exam_id, username):
    Violation.objects.filter(
        attempt__user__username=username,
        attempt__exam_id=exam_id
    ).delete()

    return Response({"status": "cleared"})


# list exam
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_exams(request):
    exams = Exam.objects.all()
    serializer = ExamDetailSerializer(exams, many=True)
    return Response(serializer.data)


# turn exam on or off
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_exam(request, exam_id):

    exam = Exam.objects.get(id=exam_id)
    exam.is_active = not exam.is_active
    exam.save()
    if not exam.is_active:
        ExamAttempt.objects.filter(
        exam=exam,
        status="active"
    ).update(status="terminated")

    return Response({"status": "toggled"})


from django.contrib.auth import get_user_model
User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_all_users(request):
    users = User.objects.all().values('id', 'username', 'first_name', 'last_name')
    return Response(list(users))

from django.shortcuts import get_object_or_404

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

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

# 1. DELETE OLD QUESTIONS FIRST
    exam.questions.all().delete()

# 2. CREATE NEW QUESTIONS
    for q in request.data.get("questions", []):
        Question.objects.create(
        exam=exam,
        text=q.get("text"),
        option_a=q.get("option_a"),
        option_b=q.get("option_b"),
        option_c=q.get("option_c"),
        option_d=q.get("option_d"),
        correct_answer=q.get("correct_answer"),
    )

    return Response({"status": "updated"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_exam(request):
    serializer = ExamSerializer(data=request.data)

    if serializer.is_valid():
        exam = serializer.save(created_by=request.user)

        return Response({
            "status": "created",
            "exam_id": exam.id
        })

    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    exam.delete()

    return Response({"status": "deleted"})

@api_view(['GET'])
def exam_qa(request, exam_id):
    questions = Question.objects.filter(exam_id=exam_id)

    data = []
    for q in questions:
        data.append({
            "id": q.id,
            "text": q.text,
            "option_a": q.option_a,
            "option_b": q.option_b,
            "option_c": q.option_c,
            "option_d": q.option_d,
            "correct_answer": q.correct_answer
        })

    return Response(data)



@api_view(['GET'])
def exam_results(request, exam_id):
    attempts = ExamAttempt.objects.filter(exam_id=exam_id).select_related('user')

    user_data = defaultdict(list)

    for a in attempts:
        user_data[a.user.username].append(a)

    data = []

    for username, attempts_list in user_data.items():
        latest = attempts_list[-1]

        data.append({
            "username": username,
            "attempts": len(attempts_list),
            "score": latest.score,
            "start_time": latest.start_time,
            "end_time": latest.end_time,
        })

    return Response(data)
