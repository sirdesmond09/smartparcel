# Generated by Django 3.0 on 2022-02-05 12:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_remove_boxlocation_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='parcel',
            name='size',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.BoxSize'),
        ),
    ]
