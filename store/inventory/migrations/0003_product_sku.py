# Generated by Django 4.2.5 on 2024-04-14 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_delivery'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='sku',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]