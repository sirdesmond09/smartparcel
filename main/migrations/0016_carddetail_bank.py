# Generated by Django 3.0 on 2022-01-26 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_carddetail'),
    ]

    operations = [
        migrations.AddField(
            model_name='carddetail',
            name='bank',
            field=models.CharField(max_length=244, null=True),
        ),
    ]