# Generated by Django 5.1.3 on 2024-12-13 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0005_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='address',
            field=models.TextField(blank=True, null=True, verbose_name='Address'),
        ),
    ]
