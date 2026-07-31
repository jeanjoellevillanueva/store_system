from datetime import timedelta
from secrets import randbelow

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from .models import EmailOTP

class OTPResendTooSoon(Exception):
    """
    Raised when a user requests another OTP before the resend cooldown ends.
    """
    pass

def generate_otp_code():
    """
    Generate a cryptographically secure six-digit numeric OTP code.
    """
    return f'{randbelow(1_000_000):06d}'

def issue_login_otp(user):
    """
    Create and email a new login OTP for a user.

    Any active unused login OTP is invalidated before the new OTP is created.
    The database stores only a password hash of the OTP, never the raw code.
    Raises OTPResendTooSoon if the user requests a new code too quickly.
    """
    now = timezone.now()
    expiry_seconds = getattr(settings, 'EMAIL_OTP_EXPIRY_SECONDS', 600)
    resend_cooldown_seconds = getattr(
        settings,
        'EMAIL_OTP_RESEND_COOLDOWN_SECONDS',
        60,
    )

    with transaction.atomic():
        locked_user = User.objects.select_for_update().get(pk=user.pk)

        active_otp = (
            EmailOTP.objects
            .select_for_update()
            .filter(
                user=locked_user,
                purpose=EmailOTP.Purpose.LOGIN,
                consumed_at__isnull=True,
                invalidated_at__isnull=True,
            )
            .first()
        )

        if active_otp and (
            now - active_otp.sent_at
        ).total_seconds() < resend_cooldown_seconds:
            raise OTPResendTooSoon(
                'Please wait before requesting another verification code.'
            )

        EmailOTP.objects.filter(
            user=locked_user,
            purpose=EmailOTP.Purpose.LOGIN,
            consumed_at__isnull=True,
            invalidated_at__isnull=True,
        ).update(invalidated_at=now)

        raw_code = generate_otp_code()

        otp = EmailOTP.objects.create(
            user=locked_user,
            purpose=EmailOTP.Purpose.LOGIN,
            code_hash=make_password(raw_code),
            expires_at=now + timedelta(seconds=expiry_seconds),
            sent_at=now,
        )

    send_mail(
        subject='Your login verification code',
        message=(
            f'Your verification code is {raw_code}. '
            f'It expires in {expiry_seconds // 60} minutes. '
            'Do not share this code with anyone.'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[locked_user.email],
        fail_silently=False,
    )

    return otp

