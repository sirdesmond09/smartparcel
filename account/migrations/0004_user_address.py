# Generated by Django 3.0 on 2021-12-15 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_auto_20211215_1743'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='address',
            field=models.CharField(blank=True, max_length=5000, null=True, verbose_name='address'),
        ),
    ]
