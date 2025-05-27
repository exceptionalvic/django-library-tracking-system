import datetime
from celery import shared_task
from .models import Loan
from django.core.mail import send_mail, mail_admins
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=5, retry_on=(Exception,))
def send_loan_notification(self, loan_id):
    try:
        loan = Loan.objects.get(id=loan_id)
        member_email = loan.member.user.email
        book_title = loan.book.title
        send_mail(
            subject='Book Loaned Successfully',
            message=f'Hello {loan.member.user.username},\n\nYou have successfully loaned "{book_title}".\nPlease return it by the due date.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[member_email],
            fail_silently=False,
        )
    except Loan.DoesNotExist:
        """Log unusual error and notify admin when Loan by id is not found"""
        logger.critical(f"Error@check_overdue_loans. Error Detail: \
                        Loan not found when running check overdue background tas")
        
        mail_admins(
            subject="Critical Error Occurred During send loan notification",
            message="Critical Error Occurred During send loan notificationr, please take a look"
        )
    except Exception as err:
        """Because this is a very vital mission critical part of this application,
        we will implement retry logic with exponential backoff logic to avoid
        overwhelming workers"""

        logger.error(f"Retrying check oerdue task... due to error {err}")

        countdown = 2 ** self.request.retries # retries after 2, 4, 8, 16

        raise self.retry(exc=err, countdown=countdown)



@shared_task(bind=True, max_retries=5, retry_on=(Exception,))
def check_overdue_loans(self, loan_id):
    try:
        today = datetime.datetime.today().date()
        all_overdue_loans = Loan.objects.filter(id=loan_id, 
                                                is_returned=False, 
                                                due_date__lt=today)
        
        for loan in all_overdue_loans:
            member_email = loan.member.user.email
            book_title = loan.book.title
            send_mail(
                subject='Your Book Loan is Overdue',
                message=f'Hello {loan.member.user.username},\n\nYou have and overdue book loan with title "{book_title}".\nPlease return it.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[member_email],
                fail_silently=False,
            )
    except Loan.DoesNotExist:
        """Log unusual error and notify admin when Loan by id is not found"""
        logger.critical(f"Error@check_overdue_loans. Error Detail: \
                        Loan not found when running check overdue background tas")
        
        mail_admins(
            subject="Critical Error Occurred During Check overdue Loan Reminder",
            message="Critical Error Occurred During Check overdue Loan Reminder, please take a look"
        )
    except Exception as err:
        """Because this is a very vital mission critical part of this application,
        we will implement retry logic with exponential backoff logic to avoid
        overwhelming workers"""

        logger.error(f"Retrying check oerdue task... due to error {err}")

        countdown = 2 ** self.request.retries # retries after 2, 4, 8, 16

        raise self.retry(exc=err, countdown=countdown)
