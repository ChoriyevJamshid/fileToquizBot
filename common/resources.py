from import_export import resources, fields
from import_export.widgets import ManyToManyWidget, ForeignKeyWidget, DateTimeWidget
from common import models


class TextResource(resources.ModelResource):

    language = fields.Field(
        attribute='language',
        column_name='language',
        widget=ForeignKeyWidget(models.Language, 'title'),
    )

    created_at = fields.Field(attribute='created_at', column_name='created_at',
                              widget=DateTimeWidget("%m/%d/%Y, %I:%M:%S %p"))
    updated_at = fields.Field(
        attribute="updated_at", column_name="updated_at", widget=DateTimeWidget("%m/%d/%Y, %I:%M:%S %p")
    )

    class Meta:
        model = models.Text
        fields = (
            'id',
            'title',
            'code',
            'order',
            'type',
            'language',
            'created_at',
            'updated_at'
        )


class LanguageResource(resources.ModelResource):
    class Meta:
        model = models.Language
        fields = (
            'id',
            'title',
            'code'
        )
