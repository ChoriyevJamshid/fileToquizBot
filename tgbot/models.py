import uuid

from django.db import models
from solo.models import SingletonModel

from .managers import TelegramUserManager


class DurationChoice(models.TextChoices):
    SECONDS_10 = "10 soniya", "10 soniya"
    SECONDS_20 = "20 soniya", "20 soniya"
    SECONDS_30 = "30 soniya", "30 soniya"
    SECONDS_40 = "40 soniya", "40 soniya"


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']
        indexes = [models.Index(fields=['created_at'])]


class TelegramProfile(BaseModel):
    chat_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    language = models.CharField(max_length=255, blank=True, null=True)

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    data = models.JSONField(blank=True, null=True)

    objects = models.Manager()
    users = TelegramUserManager()

    def save(self, *args, **kwargs):
        if not self.data:
            self.data = dict()
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'telegram_profile'
        indexes = [models.Index(fields=['chat_id'])]
        unique_together = (('chat_id', 'username'),)

    def __str__(self):
        return f'{self.username} {self.first_name} {self.last_name}'


# class Test(BaseModel):
#     telegram_profile = models.ForeignKey(TelegramProfile, on_delete=models.CASCADE,
#                                          related_name='tests')
#     players = models.ManyToManyField(TelegramProfile, related_name='players_tests', blank=True)
#     title = models.CharField(max_length=255, blank=True, null=True)
#     timer = models.IntegerField(blank=True, null=True)
#     quantity = models.IntegerField(blank=True, null=True)
#
#     test_data = models.JSONField(blank=True, null=True)
#     objects = models.Manager()
#
#     def __str__(self):
#         return self.title
#
#     @classmethod
#     def save_to_data(cls, id, user_id):
#
#         def generate_name():
#             import string
#             import random
#             name = str()
#             tpl = 'upper', 'lower'
#             for i in range(6):
#                 stm = random.choice(tpl)
#                 if stm == 'upper':
#                     name += random.choice(string.ascii_uppercase)
#                 else:
#                     name += random.choice(string.ascii_lowercase)
#             return name
#
#         test = cls.objects.filter(id=id, telegram_profile__id=user_id)
#
#         if test.exists():
#             test = test.prefetch_related("questions", "questions__options").first()
#             QUANTITY = test.quantity
#
#             if test.test_data is None:
#                 test.test_data = dict()
#
#             data = test.test_data
#             questions = test.questions.all()
#             part = None
#             for index, question in enumerate(questions):
#
#                 if part is None:
#                     part = 1
#
#                 if data.get(part) is None:
#                     part_uuid = generate_name()
#                     data[part] = dict()
#                     data[part]['tests'] = []
#                     data[part]['uuid'] = part_uuid
#
#                 options = question.options.all()
#                 correct_option = options.filter(is_correct=True).first()
#                 data[part]['tests'].append({
#                     'question': question.question,
#                     'options': tuple(options.values_list("option", flat=True)),
#                     'correct': correct_option.option,
#                 })
#
#                 if (index + 1) % QUANTITY == 0:
#                     part += 1
#             data['quantity'] = len(questions)
#             test.test_data = data
#             test.save(update_fields=['test_data'])
#         return test


class Quiz(BaseModel):
    user = models.ForeignKey(TelegramProfile, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255, blank=True, null=True)
    timer = models.IntegerField(blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)

    data = models.JSONField(blank=True, null=True)
    link = models.CharField(max_length=31, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        db_table = 'quiz'
        unique_together = (('user', 'title'),)
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class QuizPart(BaseModel):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='parts')
    link = models.CharField(max_length=255, blank=True, null=True, unique=True)
    from_number = models.IntegerField(blank=True, null=True)
    to_number = models.IntegerField(blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    data = models.JSONField(blank=True, null=True)

    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.quantity:
            self.quantity = self.to_number - self.from_number + 1

        if not self.data:
            self.data = dict()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"QuizPart(pk={self.pk}, link={self.link})"


class UserQuizPart(BaseModel):
    user = models.ForeignKey(TelegramProfile, on_delete=models.CASCADE, related_name='quiz_parts')
    quiz_part = models.ForeignKey(QuizPart, on_delete=models.CASCADE, related_name='users')
    total_answers = models.IntegerField(default=0, blank=True, null=True)
    correct_answers = models.IntegerField(default=0, blank=True, null=True)
    skipped_answers = models.IntegerField(default=0, blank=True, null=True)
    failed_answers = models.IntegerField(default=0, blank=True, null=True)
    spend_time = models.IntegerField(default=0, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    data = models.JSONField(blank=True, null=True)

    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.data:
            self.data = dict()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'UserQuiz(pk={self.pk})'


class GroupQuizPart(BaseModel):
    quiz_part = models.ForeignKey(QuizPart, on_delete=models.SET_NULL, blank=True, null=True,
                                  related_name="groups")
    data_model = models.ForeignKey("Data", on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name="groups")

    language = models.CharField(max_length=255, blank=True, null=True)
    group_id = models.IntegerField(blank=True, null=True)
    message_id = models.IntegerField(blank=True, null=True)
    index = models.IntegerField(default=0)

    data = models.JSONField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    is_finish = models.BooleanField(default=False)

    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.data:
            self.data = dict()
            self.data['users'] = dict()
            self.data['users_number'] = 0

        if not self.data_model:
            self.data_model = Data.get_solo()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"GroupQuizPart(pk = {self.pk}) group_id={self.group_id}"


class Data(SingletonModel):
    data = models.JSONField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.data:
            self.data = {}
            self.data['instruction'] = dict()
            self.data['instruction']['photo'] = dict()
            self.data['instruction']['video'] = dict()
            self.data['instruction']['photo']['word'] = ""
            self.data['instruction']['photo']['excel'] = ""
            self.data['instruction']['photo']['txt'] = ""
            self.data['instruction']['photo']['csv'] = ""
            self.data['instruction']['video']['word'] = ""
            self.data['instruction']['video']['excel'] = ""
            self.data['instruction']['video']['txt'] = ""
            self.data['instruction']['video']['csv'] = ""

            self.data['groups'] = dict()
        if not self.data.get('groups', None):
            self.data['groups'] = dict()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Data"
