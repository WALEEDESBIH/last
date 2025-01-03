# Generated by Django 5.1.2 on 2024-12-01 18:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_alter_inventorylocation_reserved'),
        ('pos', '0003_inbounditem_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='inbounditem',
            name='inventory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.inventory'),
        ),
        migrations.AddField(
            model_name='outbounditem',
            name='inventory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.inventory'),
        ),
    ]
