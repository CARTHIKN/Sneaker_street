# Generated by Django 4.2.5 on 2023-10-26 15:18

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_remove_order_address_line_1_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderproduct',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
