# Generated by Django 3.0 on 2022-02-09 18:16

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import main.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BoxLocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('center_apikey', models.CharField(blank=True, default=main.models.create_box_key, max_length=255, null=True, unique=True)),
                ('location', models.CharField(max_length=200)),
                ('center_name', models.CharField(max_length=300)),
                ('address', models.CharField(max_length=3000)),
                ('available_small_space', models.IntegerField(default=0)),
                ('available_medium_space', models.IntegerField(default=0)),
                ('available_large_space', models.IntegerField(default=0)),
                ('available_xlarge_space', models.IntegerField(default=0)),
                ('available_xxlarge_space', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='BoxSize',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large'), ('xlarge', 'Xlarge'), ('xxlarge', 'XXlarge')], max_length=255, unique=True)),
                ('length', models.FloatField()),
                ('breadth', models.FloatField()),
                ('price', models.FloatField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('spaces', models.IntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Compartment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=20)),
                ('is_available', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='compartments', to='main.Category')),
                ('size', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='compartments', to='main.BoxSize')),
            ],
        ),
        migrations.CreateModel(
            name='Payments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField()),
                ('payment_for', models.CharField(max_length=300)),
                ('reference', models.CharField(max_length=300)),
                ('currency', models.CharField(max_length=300)),
                ('transaction_date', models.DateTimeField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payments', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Parcel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=500, null=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+2341234567890'. Up to 20 digits allowed.", regex='^\\+?1?\\d{9,20}$')])),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('duration', models.CharField(blank=True, max_length=200, null=True)),
                ('address', models.CharField(blank=True, max_length=500, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('city', models.CharField(blank=True, max_length=200, null=True)),
                ('pick_up', models.CharField(blank=True, max_length=6, null=True)),
                ('drop_off', models.CharField(blank=True, max_length=6, null=True)),
                ('dropoff_used', models.BooleanField(default=False)),
                ('pickup_used', models.BooleanField(default=False)),
                ('parcel_type', models.CharField(blank=True, max_length=400, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('assigned', 'Assigned'), ('dropped', 'Dropped'), ('completed', 'Completed')], default='pending', max_length=300)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('compartment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Compartment')),
                ('delivery_partner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='account.LogisticPartner')),
                ('location', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parcels', to='main.BoxLocation')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parcels', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CardDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('authorization_code', models.CharField(max_length=255)),
                ('bin', models.CharField(max_length=250)),
                ('last4', models.CharField(max_length=255)),
                ('exp_month', models.CharField(max_length=255)),
                ('exp_year', models.CharField(max_length=255)),
                ('bank', models.CharField(max_length=244, null=True)),
                ('card_type', models.CharField(max_length=255)),
                ('country_code', models.CharField(max_length=255)),
                ('account_name', models.CharField(max_length=600, null=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cards', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='boxlocation',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Category'),
        ),
        migrations.AddField(
            model_name='boxlocation',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
