from django.db import models

from tgbot.models import BaseModel


class Language(BaseModel):
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=255, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        unique_together = (('title', 'code'),)

    def __str__(self):
        return f"{self.title}, code={self.code}"


class Text(BaseModel):
    class TextType(models.TextChoices):
        TEXT = 'TEXT'
        BUTTON = 'BUTTON'

    title = models.CharField(max_length=511)
    code = models.CharField(max_length=255, blank=True, null=True)
    order = models.IntegerField(default=0, blank=True, null=True)
    type = models.CharField(max_length=255, choices=TextType.choices, blank=True, null=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='texts')

    objects = models.Manager()

    def __str__(self):
        return self.title

    @classmethod
    def texts_data(cls):
        data = {}
        texts = cls.objects.all().select_related('language')
        for text in texts:
            code = str(text.code)
            lang = str(text.language.code)
            if data.get(code) is None:
                data[code] = {}

            if data[code].get(lang) is None:
                if text.type == cls.TextType.TEXT:
                    data[code][lang] = None
                else:
                    data[code][lang] = {}
            if text.type == cls.TextType.TEXT:
                data[code][lang] = text.title
            else:
                data[code][lang][text.order] = text.title

        return data


class RequiredChannel(BaseModel):
    title = models.CharField(max_length=255)
    username = models.CharField(max_length=255)

    objects = models.Manager()

    def __str__(self):
        return self.title


class RequiredChat(BaseModel):
    title = models.CharField(max_length=255)
    url = models.URLField(max_length=511, unique=True, help_text="For example: https://t.me/anychannel")
    username = models.CharField(max_length=255, editable=False, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.username:
            usernames = str(self.url).split('/')
            self.username = usernames[-1] if usernames[-1] != '' else usernames[-2]

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
