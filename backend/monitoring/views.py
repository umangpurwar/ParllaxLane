from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.timezone import now
from rest_framework.decorators import api_view, permission_classes
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
import cloudinary.uploader
from core.permissions import IsOrgMember
from .models import Violation, Screenshot
from exams.models import ExamAttempt

class LogViolationView(APIView):
    permission_classes = [IsOrgMember]

    @method_decorator(ratelimit(key='user', rate='10/m', method='POST', block=True))
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
        except:
            return Response({"error": "severity must be integer"}, status=400)

        org = request.user.current_organisation

        try:
            attempt = ExamAttempt.objects.get(
                id=attempt_id,
                user=request.user,
                exam__organisation=org  
            )
        except ExamAttempt.DoesNotExist:
            return Response({"error": "Invalid attempt"}, status=400)

        if attempt.status != "active":
            return Response({"error": "Exam already ended"}, status=400)

        Violation.objects.create(
            attempt=attempt,
            violation_type=violation_type,
            severity=severity,
            metadata=metadata
        )

        attempt.total_violations += 1
        attempt.risk_score += severity

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
    permission_classes = [IsOrgMember]

    @method_decorator(ratelimit(key='user', rate='2/m', method='POST', block=True))
    def post(self, request):

        attempt_id = request.data.get("attempt_id")
        image_file = request.FILES.get("image")

        if not attempt_id:
            return Response({"error": "attempt_id is required"}, status=400)
        if not image_file:
            return Response({"error": "image file is required"}, status=400)

        org = request.user.current_organisation

        try:
            attempt = ExamAttempt.objects.get(
                id=attempt_id,
                user=request.user,
                exam__organisation=org  
            )
        except ExamAttempt.DoesNotExist:
            return Response({"error": "Invalid attempt"}, status=400)

        if attempt.status != "active":
            return Response({"error": "Exam already ended"}, status=400)

        try:
            upload_result = cloudinary.uploader.upload(
                image_file,
                folder="screenshots"
            )
            image_url = upload_result.get("secure_url")

        except Exception:
            return Response({"error": "Upload failed"}, status=500)

        Screenshot.objects.create(
            attempt=attempt,
            image=image_url
        )

        return Response({
            "status": "saved",
            "url": image_url
        })

@ratelimit(key='user', rate='30/m', method='POST', block=True)
@api_view(['POST'])
@permission_classes([IsOrgMember])
def student_heartbeat(request):

    attempt_id = request.data.get("attempt_id")
    if not attempt_id:
        return Response({"error": "attempt_id required"}, status=400)

    org = request.user.current_organisation

    updated = ExamAttempt.objects.filter(
        id=attempt_id,
        user=request.user,
        exam__organisation=org   
    ).update(last_active=now())

    if not updated:
        return Response({"error": "Invalid attempt"}, status=400)

    return Response({"status": "alive"})