# Generated by Django 4.2.5 on 2024-06-11 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_product_sku'),
    ]

    operations = [
        migrations.AddField(
            model_name='delivery',
            name='running_stock',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
