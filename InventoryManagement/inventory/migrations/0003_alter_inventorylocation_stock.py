# Generated by Django 5.1.2 on 2024-11-16 12:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_color_product'),
        ('pos', '0003_inbounditem_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventorylocation',
            name='stock',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pos.inbounditem'),
        ),
    ]