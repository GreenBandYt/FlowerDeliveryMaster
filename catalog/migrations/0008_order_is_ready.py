# Generated by Django 5.1.3 on 2024-12-17 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0007_alter_order_table_alter_orderitem_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_ready',
            field=models.BooleanField(default=False, verbose_name='Order Ready'),
        ),
    ]