# Generated by Django 5.0.3 on 2024-05-08 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moduloNutricion', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='menu',
            name='menu',
            field=models.TextField(default='', max_length=100),
        ),
    ]
