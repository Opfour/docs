# Generated by Django 5.1.4 on 2025-01-18 11:53
import re

import django.contrib.postgres.fields
import django.db.models.deletion
from django.core.files.storage import default_storage
from django.db import migrations, models

from botocore.exceptions import ClientError

import core.models
from core.utils import extract_attachments


def populate_attachments_on_all_documents(apps, schema_editor):
    """Populate "attachments" field on all existing documents in the database."""
    Document = apps.get_model("core", "Document")

    for document in Document.objects.all():
        try:
            response = default_storage.connection.meta.client.get_object(
                Bucket=default_storage.bucket_name, Key=f"{document.pk!s}/file"
            )
        except (FileNotFoundError, ClientError):
            pass
        else:
            content = response["Body"].read().decode("utf-8")
            document.attachments = extract_attachments(content)
            document.save(update_fields=["attachments"])


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0019_alter_user_language_default_to_null"),
    ]

    operations = [
        # v2.0.0 was released so we can now remove BC field "is_public"
        migrations.RemoveField(
            model_name="document",
            name="is_public",
        ),
        migrations.AlterModelManagers(
            name="user",
            managers=[
                ("objects", core.models.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name="document",
            name="attachments",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=255),
                blank=True,
                default=list,
                editable=False,
                null=True,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name="document",
            name="duplicated_from",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="duplicates",
                to="core.document",
            ),
        ),
        migrations.RunPython(
            populate_attachments_on_all_documents,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
