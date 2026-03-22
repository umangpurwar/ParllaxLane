from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.http import HttpResponse

from exams.models import Exam, ExamAttempt
from monitoring.models import Screenshot, Violation

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from openpyxl import Workbook
from datetime import timedelta
from django.utils.timezone import now
from django.utils.dateparse import parse_datetime


# ================= LIVE DASHBOARD =================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def live_monitor(request, exam_id):
    data = []
    # Fetch all attempts for this exam, ordered by user and most recent
    attempts = (
        ExamAttempt.objects
        .filter(exam_id=exam_id)
        .select_related("user")
        .order_by("user_id", "-start_time", "-id")
    )

    seen_users = set()
    current_time = now()
    # Define how long we wait before marking a user as gone (e.g., 60 seconds)
    HEARTBEAT_THRESHOLD = timedelta(seconds=60)

    for attempt in attempts:
        if attempt.user_id in seen_users:
            continue
        seen_users.add(attempt.user_id)

        # 1. CALCULATE REAL-TIME STATUS
        # If last_active is within 60 seconds, they are 'active'. Otherwise, 'inactive'.
        is_online = (current_time - attempt.last_active) < HEARTBEAT_THRESHOLD
        
        # Override the DB status with the real-time presence check
        display_status = "active" if (attempt.status == 'active' and is_online) else "inactive"
        if attempt.status == 'terminated':
            display_status = 'terminated'

        # 2. GET LATEST SIGNALS
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

        # 3. BUILD PAYLOAD
        data.append({
            "username": attempt.user.username,
            "attempt_id": attempt.id,
            "violations_count": attempt.total_violations,
            "risk_score": attempt.risk_score,
            "status": display_status, # Use our calculated status
            "system_health": system_health,

            # Latest signals for the detail modal
            "latest_violation": {
                "type": latest_violation.violation_type,
                "severity": latest_violation.severity,
                "timestamp": latest_violation.timestamp
            } if latest_violation else None,
            
            "latest_screenshot": {
                "id": latest_screenshot.id,
                "image_url": latest_screenshot.image.url if latest_screenshot and latest_screenshot.image else None,
                "timestamp": latest_screenshot.timestamp
            } if latest_screenshot else None
        })

    return Response(data)


# ================= USER DETAIL =================
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


# ================= CLEAR VIOLATIONS =================
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


# ================= CREATE EXAM =================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_exam(request):

    title = request.data.get("title")
    if not title:
        return Response({"error": "title is required"}, status=400)

    duration_raw = request.data.get("duration", 30)
    try:
        duration = int(duration_raw)
    except (TypeError, ValueError):
        return Response({"error": "duration must be an integer"}, status=400)
    if duration <= 0:
        return Response({"error": "duration must be > 0"}, status=400)

    start_time_input = request.data.get("start_time")
    end_time_input = request.data.get("end_time")

    start_time = parse_datetime(start_time_input) if start_time_input else now()
    if start_time_input and not start_time:
        return Response({"error": "start_time must be ISO-8601 datetime"}, status=400)

    end_time = parse_datetime(end_time_input) if end_time_input else None
    if end_time_input and not end_time:
        return Response({"error": "end_time must be ISO-8601 datetime"}, status=400)
    if not end_time:
        end_time = start_time + timedelta(minutes=duration)

    exam = Exam.objects.create(
        title=title,
        description=request.data.get("description", ""),
        duration=duration,
        start_time=start_time,
        end_time=end_time,
        created_by=request.user
    )

    return Response({
        "status": "created",
        "exam_id": exam.id
    })


# ================= LIST EXAMS =================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_exams(request):

    exams = Exam.objects.all().values()

    return Response(exams)


# ================= TOGGLE EXAM =================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_exam(request, exam_id):

    exam = Exam.objects.get(id=exam_id)
    exam.is_active = not exam.is_active
    exam.save()

    return Response({"status": "toggled"})


# ================= PDF =================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_pdf(request, exam_id):

    attempts = ExamAttempt.objects.filter(exam_id=exam_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'

    doc = SimpleDocTemplate(response)
    styles = getSampleStyleSheet()

    elements = []

    for a in attempts:
        text = f"""
        User: {a.user} <br/>
        Violations: {a.total_violations} <br/>
        Risk: {a.risk_score} <br/>
        Status: {a.status} <br/><br/>
        """
        elements.append(Paragraph(text, styles["Normal"]))

    doc.build(elements)
    return response


# ================= EXCEL =================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_excel(request, exam_id):

    attempts = ExamAttempt.objects.filter(exam_id=exam_id)

    wb = Workbook()
    ws = wb.active

    ws.append(["User", "Violations", "Risk", "Status"])

    for a in attempts:
        ws.append([
            str(a.user),
            a.total_violations,
            a.risk_score,
            a.status
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = 'attachment; filename="report.xlsx"'

    wb.save(response)
    return response

# In admin_panel/views.py
from django.contrib.auth import get_user_model
User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_all_users(request):
    users = User.objects.all().values('id', 'username', 'first_name', 'last_name')
    return Response(list(users))
