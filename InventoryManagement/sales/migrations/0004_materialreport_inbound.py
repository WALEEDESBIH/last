# Generated by Django 5.1.2 on 2024-12-29 19:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0006_remove_inbounditem_location'),
        ('sales', '0003_alter_materialreport_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='materialreport',
            name='inbound',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pos.inbound'),
        ),
    ]