from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from . import models, resources


class TextInline(admin.TabularInline):
    extra = 0
    model = models.Text


@admin.register(models.Language)
class LanguageAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'title', 'code', 'created_at', 'updated_at')
    list_display_links = ('id', 'title')
    resource_class = resources.LanguageResource


@admin.register(models.Text)
class TextAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'cod', 'type')
    list_display_links = ('cod',)
    list_filter = ('language', 'created_at', 'updated_at')
    search_fields = ('title', 'cod__title')
    resource_class = resources.TextResource


@admin.register(models.RequiredChannel)
class RequiredChannelAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'username', 'created_at', 'updated_at')
    list_display_links = ('id', 'title')
    search_fields = ('title',)


@admin.register(models.Code)
class CodeAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'title')
    list_display_links = ('title',)
    search_fields = ('id', 'title')
    inlines = [TextInline]


@admin.register(models.Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'file_type', 'spent_time', 'is_active', 'is_sent', 'created_at')
    list_filter = ('is_active', 'is_sent')
    search_fields = ('title',)
    search_help_text = "By title"
