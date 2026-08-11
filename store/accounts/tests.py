from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password 
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core import mail
from django.test import TestCase
from django.test import override_settings
from django.utils import timezone
from django.urls import reverse

from .models import EmailOTP

from .services import OTPResendTooSoon
from .services import issue_login_otp
from .services import OTPAttemptsExceeded
from .services import OTPExpired
from .services import OTPInvalidCode
from .services import OTPNotAvailable
from .services import verify_login_otp
from .services import OTPEmailAlreadyInUse
from .services import issue_email_enrollment_otp
from .services import verify_email_enrollment_otp
from .services import create_pending_registration

from .forms import OTPVerificationForm
from .forms import RegistrationForm


# Create your tests here.
@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='no-reply@example.com',
    EMAIL_OTP_EXPIRY_SECONDS=600,
    EMAIL_OTP_RESEND_COOLDOWN_SECONDS=60,
)

class IssueLoginOTPTestCase(TestCase):
    """Tests for secure creation and delivery of login OTPs."""

    def setUp(self):
        """Create a user that requests OTPs in every test."""
        self.user = User.objects.create_user(
            username='maria',
            email='maria@example.com',
            password='safe-password',
        )

    @patch('accounts.services.generate_otp_code', return_value='123456')
    def test_issue_login_otp_creates_and_sends_otp(self, _):
        """A valid OTP request stores only a hash and sends one email."""
        otp = issue_login_otp(self.user)

        # Check that the OTP is stored in the database
        self.assertEqual(EmailOTP.objects.count(), 1)
        self.assertEqual(otp.user, self.user)
        self.assertTrue(check_password('123456', otp.code_hash))
        self.assertNotEqual(otp.code_hash, '123456')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['maria@example.com'])
        self.assertIn('123456', mail.outbox[0].body)

    @patch('accounts.services.generate_otp_code', return_value='123456')
    def test_issue_login_otp_blocks_rapid_resend(self, _):
        """A second request within the cooldown period is rejected."""
        issue_login_otp(self.user)

        with self.assertRaises(OTPResendTooSoon):
            issue_login_otp(self.user)

        self.assertEqual(EmailOTP.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    @patch('accounts.services.generate_otp_code', return_value='123456')
    def test_issue_login_otp_invalidates_previous_code_after_cooldown(self, _):
        """A later request invalidates the old OTP and creates a new one."""
        first_otp = issue_login_otp(self.user)

        EmailOTP.objects.filter(pk=first_otp.pk).update(
            sent_at=timezone.now() - timedelta(seconds=61),
        )

        second_otp = issue_login_otp(self.user)

        first_otp.refresh_from_db()
        self.assertIsNotNone(first_otp.invalidated_at)
        self.assertIsNone(second_otp.invalidated_at)
        self.assertEqual(EmailOTP.objects.count(), 2)


@override_settings(EMAIL_OTP_MAX_ATTEMPTS=5)
class VerifyLoginOTPTestCase(TestCase):
    """Tests for secure verification and one-time use of login OTPs."""

    def setUp(self):
        """Create a user that owns the OTP records used in each test."""
        self.user = User.objects.create_user(
            username='jose',
            email='jose@example.com',
            password='safe-password',
        )

    def create_active_otp(self, code='123456', expires_at=None):
        """Create a known active OTP without sending an email."""
        now = timezone.now()

        return EmailOTP.objects.create(
            user=self.user,
            purpose=EmailOTP.Purpose.LOGIN,
            code_hash=make_password(code),
            expires_at=expires_at or now + timedelta(minutes=10),
            sent_at=now,
        )

    def test_verify_login_otp_consumes_correct_code(self):
        """A correct OTP is accepted once and marked as consumed."""
        otp = self.create_active_otp()

        verified_otp = verify_login_otp(self.user, '123456')

        otp.refresh_from_db()
        self.assertEqual(verified_otp.pk, otp.pk)
        self.assertIsNotNone(otp.consumed_at)

    def test_verify_login_otp_increments_attempt_for_wrong_code(self):
        """A wrong OTP increases the failed-attempt counter."""
        otp = self.create_active_otp()

        with self.assertRaises(OTPInvalidCode):
            verify_login_otp(self.user, '000000')

        otp.refresh_from_db()
        self.assertEqual(otp.attempt_count, 1)
        self.assertIsNone(otp.invalidated_at)

    def test_verify_login_otp_rejects_expired_code(self):
        """An expired OTP is rejected and invalidated."""
        otp = self.create_active_otp(
            expires_at=timezone.now() - timedelta(seconds=1),
        )

        with self.assertRaises(OTPExpired):
            verify_login_otp(self.user, '123456')

        otp.refresh_from_db()
        self.assertIsNotNone(otp.invalidated_at)

    def test_verify_login_otp_invalidates_code_after_five_failures(self):
        """The fifth wrong attempt invalidates the OTP."""
        otp = self.create_active_otp()

        for _ in range(4):
            with self.assertRaises(OTPInvalidCode):
                verify_login_otp(self.user, '000000')

        with self.assertRaises(OTPAttemptsExceeded):
            verify_login_otp(self.user, '000000')

        otp.refresh_from_db()
        self.assertEqual(otp.attempt_count, 5)
        self.assertIsNotNone(otp.invalidated_at)

    def test_verify_login_otp_rejects_consumed_code(self):
        """A successfully used OTP cannot be used a second time."""
        self.create_active_otp()

        verify_login_otp(self.user, '123456')

        with self.assertRaises(OTPNotAvailable):
            verify_login_otp(self.user, '123456')


class OTPVerificationFormTestCase(TestCase):
    """Tests for validation of the OTP input form."""
    def test_form_accepts_six_digits_code(self):
        """A six-digit numeric OTP is valid and keeps leading zeroes."""
        form = OTPVerificationForm(data={'code': '001234'})

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['code'], '001234')

    def test_form_rejects_non_numeric_code(self):
        """An OTP containing letters is invalid."""
        form = OTPVerificationForm(data={'code': '12ab34,'})

        self.assertFalse(form.is_valid())
        self.assertIn('code', form.errors)

    def test_form_rejects_code_with_wrong_length(self):
        """An OTP must contain exactly six digits."""
        form = OTPVerificationForm(data={'code': '12345'})

        self.assertFalse(form.is_valid())
        self.assertIn('code', form.errors)


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='no-reply@example.com',
    EMAIL_OTP_EXPIRY_SECONDS=600,
    EMAIL_OTP_RESEND_COOLDOWN_SECONDS=60,
)

class EmailEnrollmentOTPTestCase(TestCase):
    """Tests for OTP issuance during legacy-user email enrollment."""

    def setUp(self):
        """Create a legacy user whose User.email is still blank."""
        self.user = User.objects.create_user(
            username='legacy-user',
            email='',
            password='safe-password',
        )

    @patch('accounts.services.generate_otp_code', return_value='123456')
    def test_enrollment_otp_uses_submitted_email(self, _):
        """Enrollment OTP is sent to and records the supplied email."""
        otp = issue_email_enrollment_otp(
            self.user,
            'Legacy.User@example.com',
        )

        self.assertEqual(otp.purpose, EmailOTP.Purpose.EMAIL_ENROLLMENT)
        self.assertEqual(otp.email, 'legacy.user@example.com')
        self.assertEqual(self.user.email, '')
        self.assertEqual(mail.outbox[0].to, ['legacy.user@example.com'])

    def test_enrollment_otp_rejects_email_already_in_use(self):
        """An email already assigned to another user cannot be enrolled."""
        User.objects.create_user(
            username='email-owner',
            email='owner@example.com',
            password='safe-password',
        )

        with self.assertRaises(OTPEmailAlreadyInUse):
            issue_email_enrollment_otp(self.user, 'owner@example.com')

    def create_enrollment_otp(self, email='legacy@example.com'):
        """Create a known enrollment OTP without sending an email."""
        now = timezone.now()

        return EmailOTP.objects.create(
            user=self.user,
            purpose=EmailOTP.Purpose.EMAIL_ENROLLMENT,
            email=email,
            code_hash=make_password('123456'),
            expires_at=now + timedelta(minutes=10),
            sent_at=now,
        )

    def test_enrollment_verification_saves_verified_email(self):
        """A correct enrollment OTP saves its verified email to the user."""
        otp = self.create_enrollment_otp('legacy@example.com')

        verify_email_enrollment_otp(self.user, '123456')

        self.user.refresh_from_db()
        otp.refresh_from_db()

        self.assertEqual(self.user.email, 'legacy@example.com')
        self.assertIsNotNone(otp.consumed_at)

    def test_enrollment_verification_rejects_email_claimed_by_another_user(self):
        """A database uniqueness conflict does not consume the OTP."""
        User.objects.create_user(
            username='existing-owner',
            email='owner@example.com',
            password='safe-password',
        )
        otp = self.create_enrollment_otp('owner@example.com')

        with self.assertRaises(OTPEmailAlreadyInUse):
            verify_email_enrollment_otp(self.user, '123456')

        otp.refresh_from_db()
        self.assertIsNone(otp.consumed_at)


@override_settings(
    AUTHENTICATION_BACKENDS=[
        'accounts.backends.EmailOrLegacyUsernameBackend',
    ],
)

class EmailOrLegacyUsernameBackendTestCase(TestCase):
    """Test email login and the temporary legacy-username path."""

    def setUp(self):
        self.email_user = User.objects.create_user(
            username='maria',
            email='Maria@example.com',
            password='safe-password',
        )
        self.legacy_user = User.objects.create_user(
            username='legacy-user',
            email='',
            password='safe-password',
        )
        self.inactive_user = User.objects.create_user(
            username='inactive-user',
            email='inactive@example.com',
            password='safe-password',
            is_active=False,
        )

    def test_authenticates_verified_user_by_email_case_insensitively(self):
        user = authenticate(
            username='MARIA@EXAMPLE.COM',
            password='safe-password',
        )

        self.assertEqual(user, self.email_user)

    def test_authenticates_legacy_user_by_username_while_email_is_blank(self):

        user = authenticate(
            username='legacy-user',
            password='safe-password',
        )

        self.assertEqual(user, self.legacy_user)

    def test_rejects_verified_user_username_login(self):
        user = authenticate(
            username='maria',
            password='safe-password',
        )

        self.assertIsNone(user)

    def test_rejects_inactive_user(self):
        user = authenticate(
            username='inactive@example.com',
            password='safe-password',
        )

        self.assertIsNone(user)


class RegistrationFormTestCase(TestCase):
    """Test new-user registration input validation."""

    def test_rejects_mismatched_passwords(self):
        form = RegistrationForm(
            data={
                'email': 'new.user@example.com',
                'password1': 'safe-password',
                'password2': 'different-password',
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='no-reply@example.com',
)
class PendingRegistrationTestCase(TestCase):
    """Test internal username generation and deferred email persistence."""

    @patch(
        'accounts.services.generate_internal_username',
        return_value='user_internal_123',
    )
    def test_creates_blank_email_user_and_enrollment_otp(self, _):
        user = create_pending_registration(
            'New.User@example.com',
            'safe-password',
        )

        user.refresh_from_db()
        otp = EmailOTP.objects.get(user=user)

        self.assertEqual(user.username, 'user_internal_123')
        self.assertEqual(user.email, '')
        self.assertTrue(user.check_password('safe-password'))
        self.assertEqual(otp.email, 'new.user@example.com')
        self.assertEqual(otp.purpose, EmailOTP.Purpose.EMAIL_ENROLLMENT)
        self.assertEqual(len(mail.outbox), 1)

    def test_rejects_an_email_already_owned_by_a_user(self):
        User.objects.create_user(
            username='existing-user',
            email='owner@example.com',
            password='safe-password',
        )

        with self.assertRaises(OTPEmailAlreadyInUse):
            create_pending_registration(
                'OWNER@example.com',
                'safe-password',
            )

@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='no-reply@example.com',
)
class RegistrationViewTestCase(TestCase):
    """Test the registration page's handoff into enrollment OTP verification"""

    @patch(
        'accounts.services.generate_internal_username',
        return_value='user_registration_123',
    )
    def test_registration_starts_email_enrollment_otp(self, _):
        response = self.client.post(
            reverse('accounts:register'),
            {
                'email': 'new.user@example.com',
                'password1': 'Strong-password-2026!',
                'password2': 'Strong-password-2026!',
            },
        )

        self.assertRedirects(response, reverse('accounts:otp_verify'))

        user = User.objects.get(username='user_registration_123')
        otp = EmailOTP.objects.get(user=user)
        session = self.client.session

        self.assertEqual(user.email, '')
        self.assertEqual(otp.email, 'new.user@example.com')
        self.assertEqual(
            session['pending_otp_user_id'],
            user.pk,
        )
        self.assertEqual(
            session['pending_otp_purpose'],
            EmailOTP.Purpose.EMAIL_ENROLLMENT,
        )
        self.assertNotIn('_auth_user_id', session)


@override_settings(
    AUTHENTICATION_BACKENDS=[
        'accounts.backends.EmailOrLegacyUsernameBackend',
    ],
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='no-reply@example.com',
)
class AuthenticationFlowIntegrationTestCase(TestCase):
    """Exercise the public authentication flow from credentials through OTP."""

    def setUp(self):
        self.password = 'Strong-password-2026!'

        self.verified_user = User.objects.create_user(
            username='verified-user',
            email='verified@example.com',
            password=self.password,
        )
        self.legacy_user = User.objects.create_user(
            username='legacy-user',
            email='',
            password=self.password,
        )

    def assert_authenticated_as(self, user):
        """Confirm Django created an authenticated session for this user."""
        self.assertEqual(
            int(self.client.session['_auth_user_id']),
            user.pk,
        )

    @patch('accounts.services.generate_otp_code', return_value='123456')
    def test_verified_email_login_requires_otp_before_session_createion(self, _):
        response = self.client.post(
            reverse('accounts:login'),
            {
                'username': 'VERIFIED@example.com',
                'password': self.password,
            },
        )

        self.assertRedirects(response, reverse('accounts:otp_verify'))
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(len(mail.outbox), 1)

        response = self.client.post(
            reverse('accounts:otp_verify'),
            {'code': '123456'},
        )

        self.assertRedirects(response, reverse('calendars:home'))
        self.assert_authenticated_as(self.verified_user)

        otp = EmailOTP.objects.get(user=self.verified_user)
        self.assertIsNotNone(otp.consumed_at)

    @patch('accounts.services.generate_otp_code', return_value='123456')
    def test_legacy_username_login_enrolls_email_then_creates_session(self, _):
        response = self.client.post(
            reverse('accounts:login'),
            {
                'username': 'legacy-user',
                'password': self.password,
            },
        )

        self.assertRedirects(response, reverse('accounts:email_enrollment'))
        self.assertNotIn('_auth_user_id', self.client.session)

        response = self.client.post(
            reverse('accounts:email_enrollment'),
            {'email': 'legacy@example.com'},
        )

        self.assertRedirects(response, reverse('accounts:otp_verify'))
        self.legacy_user.refresh_from_db()
        self.assertEqual(self.legacy_user.email, '')

        response = self.client.post(
            reverse('accounts:otp_verify'),
            {'code': '123456'},
        )

        self.assertRedirects(response, reverse('calendars:home'))
        self.legacy_user.refresh_from_db()
        self.assertEqual(self.legacy_user.email, 'legacy@example.com')
        self.assert_authenticated_as(self.legacy_user)

    @patch('accounts.services.generate_internal_username', return_value='user_new_123')
    @patch('accounts.services.generate_otp_code', return_value='123456')
    def test_registration_saves_email_only_after_otp_and_creates_session(
        self,
        _,
        __,
    ):
        response = self.client.post(
            reverse('accounts:register'),
            {
                'email': 'new.user@example.com',
                'password1': self.password,
                'password2': self.password,
            },
        )

        self.assertRedirects(response, reverse('accounts:otp_verify'))

        new_user = User.objects.get(username='user_new_123')
        self.assertEqual(new_user.email, '')
        self.assertNotIn('_auth_user_id', self.client.session)

        response = self.client.post(
            reverse('accounts:otp_verify'),
            {'code': '123456'},
        )

        self.assertRedirects(response, reverse('calendars:home'))
        new_user.refresh_from_db()
        self.assertEqual(new_user.email, 'new.user@example.com')
        self.assert_authenticated_as(new_user)

    @patch('accounts.services.generate_otp_code', return_value='123456')
    def test_resend_endpoint_observes_the_cooldown(self, _):
        response = self.client.post(
            reverse('accounts:login'),
            {
                'username': 'verified@example.com',
                'password': self.password,
            },
        )

        self.assertRedirects(response, reverse('accounts:otp_verify'))
        self.assertEqual(len(mail.outbox), 1)

        response = self.client.post(reverse('accounts:otp_resend'))

        self.assertRedirects(response, reverse('accounts:otp_verify'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(EmailOTP.objects.count(), 1)