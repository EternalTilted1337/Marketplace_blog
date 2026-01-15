from app.core.celery import celery_app


@celery_app.task
def process_new_article_notification(article_id: int, title: str):
    """
    Пример задачи для Celery.
    В реальном приложении здесь могла бы быть отправка email или push-уведомления.
    """
    print(f"Получено уведомление о новой статье!")
    print(f"ID статьи: {article_id}")
    print(f"Заголовок: {title}")
    print("Здесь могла бы быть логика отправки email...")
    return f"Уведомление для статьи {article_id} обработано."


@celery_app.task
def send_registration_email(email: str):
    """
    Отправляет email-уведомление о регистрации.
    """
    print(f"Отправка письма о регистрации на адрес: {email}")
    print("Письмо успешно 'отправлено'.")
    return f"Письмо для {email} отправлено."
