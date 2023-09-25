from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from robots.models import Robot

from orders.models import Order


def send_email(customer_email, robot_model, robot_version):
    """
    Отправляет электронное письмо заказчику с информацией о доступности робота.
    """
    subject = 'Робот доступен!'
    message = (
        f'Добрый день!\n'
        f'Недавно вы интересовались нашим роботом модели {robot_model}, версии {robot_version}.\n'
        f'Этот робот теперь в наличии. Если вам подходит этот вариант - пожалуйста, свяжитесь с нами.'
    )
    from_email = None
    recipient_list = [customer_email]
    send_mail(subject, message, from_email, recipient_list)


@receiver(post_save, sender=Robot)
def post_save_robot(instance, **kwargs):
    """
    Обработчик сигнала post_save для модели Robot.
    """

    # Получаем заказы в которых указана серия созданного робота
    orders = Order.objects.filter(robot_serial__in=[instance.serial])
    # Получаем почты ожидающих заказчиков
    customers_mails = [order.customer.email for order in orders]
    # Преобразуем серию в Модель и Версию робота
    model, version = instance.serial.split('-')
    # Отправляем письма заказчикам
    [send_email(customer_email=email, robot_model=model,
                robot_version=version) for email in customers_mails]
