import smtplib
from email.message import EmailMessage
from app.core.celery import celery_app
import os


@celery_app.task
def process_new_article_notification(article_id: int, title: str):
    """
    Пример задачи для Celery.
    В реальном приложении здесь могла бы быть отправка email или push-уведомления.
    """
    print("Получено уведомление о новой статье!")
    print(f"ID статьи: {article_id}")
    print(f"Заголовок: {title}")
    print("Здесь могла бы быть логика отправки email...")
    return f"Уведомление для статьи {article_id} обработано."


@celery_app.task
def send_registration_email(email: str):
    """
    Реальная отправка email-уведомления через SMTP (MailHog).
    """
    smtp_host = os.getenv("SMTP_HOST", "127.0.0.1")
    smtp_port = int(os.getenv("SMTP_PORT", 1025))

    msg = EmailMessage()
    msg["Subject"] = "Регистрация в Marketplace Blog"
    msg["From"] = "admin@marketplace.com"
    msg["To"] = email
    msg.set_content(
        f"Поздравляем! Вы успешно зарегистрированы на нашей платформе с адресом {email}."
    )

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.send_message(msg)
        print(f"Успешно отправлено письмо на {email}")
        return f"Email sent to {email}"
    except Exception as e:
        print(f"Ошибка при отправке почты: {e}")
        return f"Error: {e}"
