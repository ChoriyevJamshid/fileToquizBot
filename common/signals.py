from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import Notification
from .tasks import send_notification


@receiver(post_save, sender=Notification)
def post_save_notification(sender, instance: Notification, created: bool, **kwargs):

    if created:
        instance.title = f"{instance.__class__.__name__} - {instance.pk}"
        instance.save()

    if created and instance.is_active and not instance.is_sent:
        send_notification(instance.pk)



