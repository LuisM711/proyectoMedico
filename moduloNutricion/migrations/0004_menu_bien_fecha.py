# Generated by Django 5.0.3 on 2024-05-12 02:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moduloNutricion', '0003_alter_menu_bien_id_cita'),
    ]

    operations = [
        migrations.AddField(
            model_name='menu_bien',
            name='fecha',
            field=models.DateField(auto_now_add=True, default=datetime.date(2024, 5, 12)),
            preserve_default=False,
        ),
    ]