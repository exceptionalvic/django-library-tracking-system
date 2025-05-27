from django.test import TestCase, TransactionTestCase
from celery.contrib.testing.worker import start_worker
from library.models import Author, Loan
from library_system.celery import app
from unittest.mock import patch
from django.test import override_settings


class CeleryIntegrationTest(TransactionTestCase):

    @classmethod
    def setUpClass(cls):
        """Setup temporary celery worker for testing in production grade"""
        cls.celery_worker = start_worker(app, perform_ping_check=False)
        cls.celery_worker = cls.celery_worker.__enter__()

    @classmethod
    def tearDownClass(cls):
        """Setup temporary celery worker for testing in production grade"""
        cls.celery_worker = cls.celery_worker.__exit__(None, None, None)

    
    def setUp(self):
        self.author = Author.objects.create(
            first_name = "Mark",
            last_name = "Twain",
            biography = "Mark Twain is a renowned novelist of the 20th Century"
        )

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @patch('library.tasks.send_mail')
    def test_loan_overdue_notification_success(self, mock_send_email):
        # implement test
        loan = Loan.objects.create()
        


    
