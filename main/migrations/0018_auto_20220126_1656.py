# Generated by Django 3.0 on 2022-01-26 15:56

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0017_auto_20220126_1623'),
    ]

    operations = [
        migrations.AddField(
            model_name='carddetail',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2022, 1, 26, 15, 56, 42, 809001, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='carddetail',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cards', to=settings.AUTH_USER_MODEL),
        ),
    ]
