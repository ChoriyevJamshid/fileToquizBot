from django.contrib import admin
from solo.admin import SingletonModelAdmin
from . import models


class QuizPartInline(admin.TabularInline):
    model = models.QuizPart
    extra = 0


@admin.register(models.TelegramProfile)
class TelegramProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat_id', 'first_name', 'last_name', 'username', 'language', 'is_verified', 'is_admin')
    list_display_links = ('id', 'chat_id')
    list_editable = ('is_admin', 'is_verified')


# @admin.register(models.Test)
# class TestAdmin(admin.ModelAdmin):
#     list_display = ('id', 'title', 'telegram_profile', 'timer', 'created_at', 'updated_at')
#     list_display_links = ('id', 'title')
#     search_fields = ('title', 'telegram_profile')


@admin.register(models.Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'timer', 'quantity', 'link', 'created_at', 'updated_at')
    list_display_links = ('id', 'title')
    inlines = [QuizPartInline, ]


@admin.register(models.UserQuizPart)
class UserQuizPartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'quiz_part', 'total_answers', 'correct_answers')


# @admin.register(models.Question)
# class QuestionAdmin(admin.ModelAdmin):
#     list_display = ('id', 'question', 'test', 'created_at', 'updated_at')
#     list_display_links = ('id', 'question')
#     search_fields = ('question', 'test')
#
#
# @admin.register(models.Option)
# class OptionAdmin(admin.ModelAdmin):
#     list_display = ('id', 'option', 'question', 'created_at', 'updated_at')
#     list_display_links = ('id', 'option')
#     search_fields = ('option', 'question')

@admin.register(models.Data)
class DataAdmin(SingletonModelAdmin):
    pass
