# Generated by Django 4.2.5 on 2023-10-21 14:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_invoice'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Invoice',
        ),
    ]
