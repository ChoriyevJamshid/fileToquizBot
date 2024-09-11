from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from solo.admin import SingletonModelAdmin
from . import models, resources


class QuizPartInline(admin.TabularInline):
    model = models.QuizPart
    extra = 0


@admin.register(models.TelegramProfile)
class TelegramProfileAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'chat_id', 'first_name', 'username', 'language', 'quiz_number', 'is_verified', 'is_notif', 'is_admin')
    list_display_links = ('id', 'chat_id')
    list_editable = ('is_admin', 'is_verified', 'is_notif')
    resource_class = resources.TelegramProfileResource
    actions = ['change_coupons_number_to_3', 'change_coupons_number_to_4', 'change_coupons_number_to_5']

    @staticmethod
    @admin.action(description="Change coupons number to 3")
    def change_coupons_number_to_3(modeladmin, request, queryset):
        queryset.update(quiz_number=3)

    @staticmethod
    @admin.action(description="Change coupons number to 4")
    def change_coupons_number_to_4(modeladmin, request, queryset):
        queryset.update(quiz_number=4)

    @staticmethod
    @admin.action(description="Change coupons number to 5")
    def change_coupons_number_to_5(modeladmin, request, queryset):
        queryset.update(quiz_number=5)



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
