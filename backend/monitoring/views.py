from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now
from rest_framework.decorators import api_view, permission_classes

from .models import Violation, Screenshot
from exams.models import ExamAttempt

class LogViolationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        attempt_id = request.data.get("attempt_id")
        violation_type = request.data.get("type")
        severity = request.data.get("severity", 1)
        metadata = request.data.get("metadata", {})

        if not attempt_id:
            return Response({"error": "attempt_id is required"}, status=400)
        if not violation_type:
            return Response({"error": "type is required"}, status=400)
        try:
            severity = int(severity)
        except (TypeError, ValueError):
            return Response({"error": "severity must be an integer"}, status=400)
        if severity < 1:
            return Response({"error": "severity must be >= 1"}, status=400)
        if metadata is None:
            metadata = {}

        try:
            attempt = ExamAttempt.objects.get(
                id=attempt_id,
                user=request.user
            )
        except ExamAttempt.DoesNotExist:
            return Response({"error": "Invalid attempt"}, status=400)
        
        if attempt.status != "active":
            return Response({"error": "Exam already ended"}, status=400)

        # Create violation
        Violation.objects.create(
            attempt=attempt,
            violation_type=violation_type,
            severity=severity,
            metadata=metadata
        )

        # Update attempt stats
        attempt.total_violations += 1
        attempt.risk_score += severity

        # Auto terminate logic
        exam = attempt.exam

        if exam.auto_submit_on_violation:
            if attempt.total_violations >= exam.violation_limit:
                attempt.status = "terminated"
                attempt.end_time = now()

        attempt.save()

        return Response({
            "status": "logged",
            "violations": attempt.total_violations,
            "risk": attempt.risk_score,
            "state": attempt.status
        })

class ScreenshotUploadView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        attempt_id = request.data.get("attempt_id")
        image = request.data.get("image")

        if not attempt_id:
            return Response({"error": "attempt_id is required"}, status=400)
        if not image:
            return Response({"error": "image is required"}, status=400)

        try:
            attempt = ExamAttempt.objects.get(
                id=attempt_id,
                user=request.user
            )
        except ExamAttempt.DoesNotExist:
            return Response({"error": "Invalid attempt"}, status=400)

        if attempt.status != "active":
            return Response({"error": "Exam already ended"}, status=400)

        Screenshot.objects.create(
            attempt=attempt,
            image=image
        )

        return Response({"status": "saved"})



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def student_heartbeat(request):
    attempt_id = request.data.get("attempt_id")
    if not attempt_id:
        return Response({"error": "attempt_id required"}, status=400)

    
    ExamAttempt.objects.filter(id=attempt_id, user=request.user).update(last_active=now())
    return Response({"status": "alive"})