from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from solo.admin import SingletonModelAdmin
from . import models, resources


class QuizPartInline(admin.TabularInline):
    model = models.QuizPart
    extra = 0


@admin.register(models.TelegramProfile)
class TelegramProfileAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'chat_id', 'first_name', 'username', 'language', 'is_verified', 'is_notif', 'is_admin')
    list_display_links = ('id', 'chat_id')
    list_editable = ('is_admin', 'is_verified', 'is_notif')
    resource_class = resources.TelegramProfileResource


# @admin.register(models.Test)
# class TestAdmin(admin.ModelAdmin):
#     list_display = ('id', 'title', 'telegram_profile', 'timer', 'created_at', 'updated_at')
#     list_display_links = ('id', 'title')
#     search_fields = ('title', 'telegram_profile')


@admin.register(models.Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'timer', 'quantity', 'link', 'created_at', 'updated_at')
    list_display_links = ('id', 'title')
    list_editable = ("timer",)
    inlines = [QuizPartInline, ]


@admin.register(models.UserQuizPart)
class UserQuizPartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'quiz_part', 'total_answers', 'correct_answers')


@admin.register(models.GroupQuizPart)
class GroupQuizPartAdmin(admin.ModelAdmin):
    list_display = ('id', 'quiz_part', 'group_id', 'message_id', 'is_active', 'is_finish')
    list_display_links = ('id', 'quiz_part', 'group_id')


@admin.register(models.QuizPart)
class QuizPartAdmin(admin.ModelAdmin):
    list_display = ('link', 'quiz', 'from_number', 'to_number', 'quantity')


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
