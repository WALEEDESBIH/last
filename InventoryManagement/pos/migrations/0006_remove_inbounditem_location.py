# Generated by Django 5.1.2 on 2024-12-28 15:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0005_alter_inbounditem_expiration_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inbounditem',
            name='location',
        ),
    ]
