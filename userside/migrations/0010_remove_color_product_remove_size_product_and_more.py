# Generated by Django 4.2.5 on 2023-10-10 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userside', '0009_color'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='color',
            name='product',
        ),
        migrations.RemoveField(
            model_name='size',
            name='product',
        ),
        migrations.AddField(
            model_name='product',
            name='colors',
            field=models.ManyToManyField(blank=True, related_name='products', to='userside.color'),
        ),
        migrations.AddField(
            model_name='product',
            name='sizes',
            field=models.ManyToManyField(blank=True, related_name='products', to='userside.size'),
        ),
    ]
