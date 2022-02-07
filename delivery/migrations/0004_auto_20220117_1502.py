# Generated by Django 3.0 on 2022-01-17 14:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_auto_20220117_1403'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('delivery', '0003_designatedparcel_date_assigned'),
    ]

    operations = [
        migrations.AlterField(
            model_name='designatedparcel',
            name='delivery_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='designated', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='designatedparcel',
            name='parcel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Parcel'),
        ),
    ]
