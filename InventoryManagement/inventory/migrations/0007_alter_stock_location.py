# Generated by Django 5.1.2 on 2024-12-30 10:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_remove_inventorylocation_quantity_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.inventorylocation'),
        ),
    ]
