# Generated by Django 4.2.5 on 2023-10-27 03:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('userside', '0015_addressbook'),
        ('orders', '0010_alter_orderproduct_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shipping_address',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='userside.addressbook'),
        ),
    ]
