import re

from django.core.validators import FileExtensionValidator
from django.db import models
from ckeditor.fields import RichTextField

from tgbot.models import BaseModel

def clean_html_for_telegram(text):
    allowed_tags = {'p', 'b', 'i', 'u', 's', 'code', 'pre', 'br', 'a', 'em', 'strong', '\\n'}

    allowed_tags_re = '|'.join(allowed_tags)
    pattern = re.compile(r'</?(?!/?(?:{}))\w+[^>]*>'.format(allowed_tags_re), re.IGNORECASE)

    clean_text = re.sub(pattern, '', text)
    return clean_text.replace('<br>', '\n').replace('&nbsp;', '') \
        .replace('<br />', '').replace('&#39;', "'") \
        .replace('<p>', '').replace('</p>', '\n').replace('\r\n\r\n', '')


class FileTypeChoice(models.TextChoices):
    VIDEO = 'video'
    PHOTO = 'photo'
    AUDIO = 'audio'


class Language(BaseModel):
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=255, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        unique_together = (('title', 'code'),)

    def __str__(self):
        return f"{self.title}, code={self.code}"


class Code(BaseModel):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Text(BaseModel):
    class TextType(models.TextChoices):
        TEXT = 'TEXT'
        BUTTON = 'BUTTON'

    title = RichTextField()
    code = models.CharField(max_length=255, blank=True, null=True)
    cod = models.ForeignKey(Code, on_delete=models.CASCADE, blank=True, null=True)
    order = models.IntegerField(default=0, blank=True, null=True)
    type = models.CharField(max_length=255, choices=TextType.choices, blank=True, null=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='texts')

    objects = models.Manager()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.cod.title

        super().save(*args, **kwargs)

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
                data[code][lang] = clean_html_for_telegram(text.title)
            else:
                data[code][lang][text.order] = clean_html_for_telegram(text.title)

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


class Notification(BaseModel):

    title = models.CharField(max_length=255, blank=True, null=True)
    content = RichTextField()
    file = models.FileField(upload_to='notifications/', blank=True, null=True,
                            validators=[FileExtensionValidator([
                                'png', 'jpg', 'jpeg', 'gif',
                                'mp4', 'mpeg', 'avi', 'webm',
                                'mp3', 'wav', 'oog', 'wv', 'wma'
                            ])])
    ids = models.CharField(max_length=4095, blank=True, null=True)
    file_id = models.CharField(max_length=255, blank=True, null=True)
    file_type = models.CharField(max_length=31, choices=FileTypeChoice.choices,
                                 blank=True, null=True, editable=False)
    is_active = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False, editable=False)
    spent_time = models.TimeField(blank=True, null=True)
    data = models.JSONField(blank=True, null=True, editable=False)

    objects = models.Manager()

    class Meta:
        db_table = 'notification'
        verbose_name = 'Notification'
        verbose_name_plural = "Notifications"
        ordering = ('-created_at',)

    def __str__(self):
        return self.title if self.title else f"Notification(pk = {self.pk})"

    def save(self, *args, **kwargs):

        if not self.file_type:
            try:
                extension = self.file.name.split('.')[-1]
                if extension in ('png', 'jpg', 'jpeg', 'gif'):
                    self.file_type = FileTypeChoice.PHOTO
                elif extension in ('mp4', 'mpeg', 'avi', 'webm'):
                    self.file_type = FileTypeChoice.VIDEO
                elif extension in ('mp3', 'wav', 'oog', 'wv', 'wma'):
                    self.file_type = FileTypeChoice.AUDIO
            except Exception as e:
                pass
        # self.content = clean_html_for_telegram(self.content)
        super().save(*args, **kwargs)

    def is_sent_save(self, spent_time):
        self.spent_time = spent_time
        super().save()




















