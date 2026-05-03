from django.db import models
from django.conf import settings

from django.db import models
from django.conf import settings


class Organisation(models.Model):

    PLAN_FREE = "free"
    PLAN_PRO = "pro"
    PLAN_ENTERPRISE = "enterprise"

    PLAN_CHOICES = [
        (PLAN_FREE, "Free"),
        (PLAN_PRO, "Pro"),
        (PLAN_ENTERPRISE, "Enterprise"),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default=PLAN_FREE
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='owned_orgs'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    # limits
    max_exams = models.IntegerField(default=3)
    max_candidates = models.IntegerField(default=30)

    max_admins = models.IntegerField(default=0)
    max_invigilators = models.IntegerField(default=0)

    proctoring_enabled = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.pk:
            self._apply_plan_limits()
        else:
            old = Organisation.objects.filter(pk=self.pk).first()
            if old and old.plan != self.plan:
                self._apply_plan_limits()

        super().save(*args, **kwargs)

    def _apply_plan_limits(self):
        if self.plan == self.PLAN_FREE:
            self.max_exams = 3
            self.max_candidates = 30
            self.max_admins = 0
            self.max_invigilators = 0
            self.proctoring_enabled = False

        elif self.plan == self.PLAN_PRO:
            self.max_exams = -1
            self.max_candidates = 200
            self.max_admins = 3
            self.max_invigilators = 5
            self.proctoring_enabled = True

        elif self.plan == self.PLAN_ENTERPRISE:
            self.max_exams = -1
            self.max_candidates = -1
            self.max_admins = -1
            self.max_invigilators = -1
            self.proctoring_enabled = True

    def __str__(self):
        return f"{self.name} ({self.plan})"


class OrganisationMember(models.Model):

    ROLE_OWNER = "owner"
    ROLE_ADMIN = "admin"
    ROLE_INVIGILATOR = "invigilator"
    ROLE_CANDIDATE = "candidate"

    ROLE_CHOICES = [
        (ROLE_OWNER, "Owner"),
        (ROLE_ADMIN, "Admin"),
        (ROLE_INVIGILATOR, "Invigilator"),
        (ROLE_CANDIDATE, "Candidate"),
    ]

    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name='members'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='memberships'
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('organisation', 'user')

    def __str__(self):
        return f"{self.user} @ {self.organisation} ({self.role})"

class OrganisationMember(models.Model):

    ROLE_OWNER = "owner"
    ROLE_ADMIN = "admin"
    ROLE_INVIGILATOR = "invigilator"
    ROLE_CANDIDATE = "candidate"

    ROLE_CHOICES = [
        (ROLE_OWNER, "Owner"),
        (ROLE_ADMIN, "Admin"),
        (ROLE_INVIGILATOR, "Invigilator"),
        (ROLE_CANDIDATE, "Candidate"),
    ]

    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name='members'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='memberships'
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('organisation', 'user')

    def __str__(self):
        return f"{self.user} @ {self.organisation} ({self.role})"
    
class OrganisationInvite(models.Model):
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name="invites"
    )
    email = models.EmailField()
    role = models.CharField(max_length=20, default="candidate")
    token = models.CharField(max_length=100, unique=True)

    accepted = models.BooleanField(default=False)

    expires_at = models.DateTimeField(null=True, blank=True)
    is_revoked = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} -> {self.organisation}"