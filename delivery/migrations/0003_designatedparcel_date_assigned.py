# Generated by Django 3.0 on 2021-12-25 09:33

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0002_designatedparcel_delivery_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='designatedparcel',
            name='date_assigned',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2021, 12, 25, 9, 33, 13, 51288, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
