# Generated by Django 4.2.5 on 2023-10-11 10:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Delivery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('product_id', models.CharField(max_length=255)),
                ('product_item_code', models.CharField(max_length=255)),
                ('product_name', models.CharField(max_length=255)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('reason', models.CharField(choices=[('deliver', 'Deliver'), ('returned', 'Returned Item'), ('pull_out', 'Pull-out'), ('void', 'Void')], default='deliver', max_length=50)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'deliveries',
            },
        ),
    ]
