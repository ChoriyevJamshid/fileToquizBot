from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from . import models, resources


@admin.register(models.Language)
class LanguageAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'title', 'code', 'created_at', 'updated_at')
    list_display_links = ('id', 'title')
    resource_class = resources.LanguageResource


@admin.register(models.Text)
class TextAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'title', 'type', 'code', 'created_at', 'updated_at')
    list_display_links = ('id', 'title')
    list_filter = ('language', 'created_at', 'updated_at')
    search_fields = ('title', 'code')
    resource_class = resources.TextResource


@admin.register(models.RequiredChannel)
class RequiredChannelAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'username', 'created_at', 'updated_at')
    list_display_links = ('id', 'title')
    search_fields = ('title', )
