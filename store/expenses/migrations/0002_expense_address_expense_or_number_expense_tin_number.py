# Generated by Django 4.2.5 on 2024-10-29 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='address',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='expense',
            name='or_number',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='expense',
            name='tin_number',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
