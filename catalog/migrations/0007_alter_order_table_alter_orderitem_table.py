# Generated by Django 5.1.3 on 2024-12-17 02:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0006_order_address'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='order',
            table='catalog_order',
        ),
        migrations.AlterModelTable(
            name='orderitem',
            table='catalog_orderitem',
        ),
    ]