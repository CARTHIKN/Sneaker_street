# Generated by Django 4.2.5 on 2023-10-12 14:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userside', '0010_remove_color_product_remove_size_product_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='colors',
        ),
        migrations.RemoveField(
            model_name='product',
            name='sizes',
        ),
        migrations.DeleteModel(
            name='Color',
        ),
        migrations.DeleteModel(
            name='Size',
        ),
    ]
