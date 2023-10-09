# Generated by Django 4.2.5 on 2023-10-07 12:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('receipt_number', models.CharField(editable=False, max_length=20)),
                ('product_id', models.CharField(max_length=255)),
                ('product_name', models.CharField(max_length=255)),
                ('capital', models.DecimalField(decimal_places=2, max_digits=10)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.PositiveIntegerField()),
                ('discount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('profit', models.DecimalField(decimal_places=2, max_digits=10)),
                ('amount_paid', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('payment_method', models.CharField(choices=[('bank_transfer', 'Bank Transfer'), ('cash', 'Cash'), ('credit', 'Credit Card')], default='cash', max_length=50)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
