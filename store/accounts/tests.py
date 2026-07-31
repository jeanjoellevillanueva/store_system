from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.test import override_settings
from django.utils import timezone

from .models import EmailOTP
from .services import OTPResendTooSoon
from .services import issue_login_otp



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
