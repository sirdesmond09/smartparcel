# Generated by Django 3.0 on 2021-11-25 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20211125_1725'),
    ]

    operations = [
        migrations.AddField(
            model_name='customertocustomer',
            name='drop_off',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
        migrations.AddField(
            model_name='customertocustomer',
            name='pick_up',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]
