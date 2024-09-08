from django.db import models
from django.utils import timezone

from tgbot.models import TelegramProfile


async def get_users_statistics() -> dict:
    return TelegramProfile.objects.all().aggregate(
        count=models.Count('id', distinct=True),
        day_count=models.Count(
            'id', filter=models.Q(created_at__gt=timezone.now() - timezone.timedelta(days=1)), distinct=True),
        week_count=models.Count(
            'id', filter=models.Q(created_at__gt=timezone.now() - timezone.timedelta(weeks=1)), distinct=True),
        month_count=models.Count(
            'id', filter=models.Q(created_at__gt=timezone.now() - timezone.timedelta(days=30)), distinct=True),

    )
