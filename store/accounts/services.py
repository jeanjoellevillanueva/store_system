from datetime import timedelta
from secrets import randbelow, token_urlsafe

from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db import transaction
from django.utils import timezone

from .models import EmailOTP

from django.core.exceptions import ValidationError
from django.core.validators import validate_email


class OTPResendTooSoon(Exception):
    """Raised when a user requests another OTP before the resend cooldown ends."""


class OTPVerificationError(Exception):
    """Base class for OTP verification failures."""


class OTPNotAvailable(OTPVerificationError):
    """Raised when no active OTP is available for verification."""


class OTPExpired(OTPVerificationError):
    """Raised when the submitted OTP has expired."""


class OTPInvalidCode(OTPVerificationError):
    """Raised when the submitted OTP does not match the stored hash."""


class OTPAttemptsExceeded(OTPVerificationError):
    """Raised when an OTP reaches the maximum number of failed attempts."""

class OTPEmailRequired(Exception):
    """Raised when an OTP is requested without an email address."""

class OTPEmailInvalid(Exception):
    """Raised when an OTP is requested with an invalid email address."""

class OTPEmailAlreadyInUse(Exception):
    """Raised when another user already owns the requested email address."""

def generate_otp_code():
    """Generate a cryptographically secure six-digit numeric OTP code."""
    return f'{randbelow(1_000_000):06d}'

def normalize_email(email):
    """Normalize and validate an email address before OTP delivery."""
    normalized_email = (email or '').strip().lower()

    if not normalized_email:
        raise OTPEmailRequired('An email address is required.')

    try:
        validate_email(normalized_email)
    except ValidationError as error:
        raise OTPEmailInvalid('Enter a valid email address.') from error

    return normalized_email



def generate_internal_username():
    """Generate an opaque username for users who register by email."""
    return f'user_{token_urlsafe(18)}'

def create_pending_registration(email, raw_password):
    """
    Create a new user with a generated username and blank User.email.

    The submitted email is stored only on the enrollment OTP. It is copied to 
    User.email by verify_email_enrollment_otp() after successful verification
    """
    normalized_email = normalize_email(email)

    if User.objects.filter(email__iexact=normalized_email).exists():
        raise OTPEmailAlreadyInUse(
            'This email address is already associated with another account.'
        )

    for _ in range(3):
        username = generate_internal_username()

        try:
            user = User.objects.create_user(
                username=username,
                email='',
                password=raw_password,
            )
        except IntegrityError:
            # A generated username collision is extremely unlikely; retry safely.
            continue

        try:
            issue_email_enrollment_otp(user, normalized_email)
        except Exception:
            # Avoid leaving a blank-email account when OTP delivery fails.
            user.delete()
            raise

        return user

    raise RuntimeError('Could not generate a unique internal username.')



def issue_login_otp(user):
    """
    Issue an OTP for a user who already has a verified login email.

    Legacy users without an email must use issue_email_enrollment_otp first.
    """
    return issue_otp(
        user=user,
        email=user.email,
        purpose=EmailOTP.Purpose.LOGIN,
    )

def issue_email_enrollment_otp(user, email):
    """
    Issue an OTP that verifies an email for a legacy username user.

    The email is saved on the OTP record first. It is saved to User.email only
    after the user submits the correct OTP.
    """
    normalized_email = normalize_email(email)

    if (
        User.objects
        .filter(email__iexact=normalized_email)
        .exclude(pk=user.pk)
        .exists()
    ): 
        raise OTPEmailAlreadyInUse(
            'This email address is already associated with another account.'
        )

    return issue_otp(
        user=user,
        email=normalized_email,
        purpose=EmailOTP.Purpose.EMAIL_ENROLLMENT,
    )

def issue_otp(user, email, purpose):
    """
    Create and email a hashed OTP for the given purpose and target email.

    A resend to the same email observes the cooldown. Changing the enrollment
    email invalidates the old code and allows a new verification email.
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
                purpose=purpose,
                consumed_at__isnull=True,
                invalidated_at__isnull=True,
            )
            .first()
        )

        is_same_email = (
            active_otp
            and active_otp.email.casefold() == email.casefold()
        )

        if active_otp and is_same_email and (
            now - active_otp.sent_at    
        ).total_seconds() < resend_cooldown_seconds:
            raise OTPResendTooSoon(
                'Please wait before requesting another verification code.'
            )

        EmailOTP.objects.filter(
            user=locked_user,
            purpose=purpose,
            consumed_at__isnull=True,
            invalidated_at__isnull=True,
        ).update(invalidated_at=now)

        raw_code = generate_otp_code()

        otp = EmailOTP.objects.create(
             user=locked_user,
            purpose=purpose,
            email=email,
            code_hash=make_password(raw_code),
            expires_at=now + timedelta(seconds=expiry_seconds),
            sent_at=now,
        )

    subject = (
        'Verify your email address'
        if purpose == EmailOTP.Purpose.EMAIL_ENROLLMENT
        else 'Your login verification code'
    )

    send_mail(
        subject=subject,
        message=(
            f'Your verification code is: {raw_code}\n\n'
            f'It expires in {expiry_seconds // 60} minutes.'
            'Do not share this code with anyone.'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

    return otp


def verify_otp(user, raw_code, purpose, on_success=None):
    """
    Verify an active OTP for a specific purpose.

    Failed attempts and invalidations are committed before an error is raised.
    The optional on_success callback runs inside the same transaction as OTP
    consumption, so related updates either both succeed or both roll back.
    """
    now = timezone.now()
    max_attempts = getattr(settings, 'EMAIL_OTP_MAX_ATTEMPTS', 5)
    verification_error = None
    verified_otp = None

    with transaction.atomic():
        locked_user = User.objects.select_for_update().get(pk=user.pk)

        otp = (
            EmailOTP.objects
            .select_for_update()
            .filter(
                user=locked_user,
                purpose=purpose,
                consumed_at__isnull=True,
                invalidated_at__isnull=True,
            )
            .order_by('-created_at')
            .first()
        )

        if otp is None:
            verification_error = OTPNotAvailable(
                'No active verification code is available.'
            )

        elif now >= otp.expires_at:
            otp.invalidated_at = now
            otp.save(update_fields=['invalidated_at'])
            verification_error = OTPExpired(
            'This verification code has expired.'
        )

        elif not check_password(raw_code, otp.code_hash):
            otp.attempt_count += 1

            update_fields = ['attempt_count']
            if otp.attempt_count >= max_attempts:
                otp.invalidated_at = now
                update_fields.append('invalidated_at')
                verification_error = OTPAttemptsExceeded(
                    'Too many incorrect verification attempts.'
                )
            else:
                verification_error = OTPInvalidCode(
                    'The verification code is incorrect.'
                )

            otp.save(update_fields=update_fields)

        else:
            if on_success:
                on_success(locked_user, otp)

            otp.consumed_at = now
            otp.save(update_fields=['consumed_at'])
            verified_otp = otp

    if verification_error:
        raise verification_error

    return verified_otp

def verify_login_otp(user, raw_code):
    """Verify and consume an OTP issued during a normal email login."""
    return verify_otp(
        user=user,
        raw_code=raw_code,
        purpose=EmailOTP.Purpose.LOGIN,
    )

def verify_email_enrollment_otp(user, raw_code):
    """
    Verify a legacy user's chosen email and save it as their login email.

    If another user receives the same email first, the database rejects the
    update and the OTP remains unconsumed.
    """

    def save_verified_email(locked_user, otp):
         """Save the email that was verified by this specific OTP."""
         locked_user.email = otp.email
         locked_user.save(update_fields=['email'])

    try:
        return verify_otp(
            user=user,
            raw_code=raw_code,
            purpose=EmailOTP.Purpose.EMAIL_ENROLLMENT,
            on_success=save_verified_email,
        )
    except IntegrityError as error:
        raise OTPEmailAlreadyInUse(
            'This email address is already associated with another account.'
        ) from error
