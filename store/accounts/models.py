from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.db.models.functions import Lower

class Employee(models.Model):
    """
    Describes the data about employee metadata.
    """

    FULLFILMENT = 'fullfilment'
    LOGISTICS = 'logistics'
    DEV = 'dev'
    SALES = 'sales'
    ADMIN = 'admin'
    ACCOUNTING = 'accounting'

    DEPARTMENT_CHOICES = [
        (FULLFILMENT, 'Fullfilment'),
        (LOGISTICS, 'Logistics'),
        (DEV, 'Developers'),
        (SALES, 'Sales & Marketing'),
        (ADMIN, 'HR & Admin'),
        (ACCOUNTING, 'Accounting'),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='employee')
    base_pay = models.DecimalField(max_digits=10, decimal_places=2)
    designation = models.CharField(max_length=100, default='')
    department = models.CharField(
        max_length=100, choices=DEPARTMENT_CHOICES, default=FULLFILMENT)


class EmailOTP(models.Model):
    class Purpose(models.TextChoices):
        LOGIN = 'login', 'Login'
        EMAIL_ENROLLMENT = 'email_enrollment', 'Email Enrollment'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='email_otps',
    )
    purpose = models.CharField(
        max_length=20,
        choices=Purpose.choices,
        default=Purpose.LOGIN,
    )
    email = models.EmailField(
        blank=True,
        default='',
    )
    code_hash = models.CharField(max_length=128)
    expires_at = models.DateTimeField()
    attempt_count = models.PositiveSmallIntegerField(default=0)
    consumed_at = models.DateTimeField(null=True, blank=True)
    invalidated_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
        # One active OTP per user and purpose.
        models.UniqueConstraint(
            fields=['user', 'purpose'],
            condition=Q(
                consumed_at__isnull=True,
                invalidated_at__isnull=True,
            ),
            name='one_active_email_otp_per_user_and_purpose',
        ),

        # One active email-enrollment OTP per email address.
        models.UniqueConstraint(
            Lower('email'),
            condition=Q(
                purpose='email_enrollment',
                consumed_at__isnull=True,
                invalidated_at__isnull=True,
            ),
            name='one_active_enrollment_otp_per_email_ci',
        ),
        ]

        indexes = [
            models.Index(fields=['user', 'purpose', 'expires_at']),
        ]

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    def __str__(self):
        return f'{self.user.email} - {self.purpose}'