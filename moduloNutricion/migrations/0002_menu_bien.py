# Generated by Django 5.0.3 on 2024-05-08 21:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moduloNutricion', '0001_initial'),
        ('moduloPrincipal', '0002_especialidades_asignacion_menu'),
    ]

    operations = [
        migrations.CreateModel(
            name='Menu_Bien',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('menu', models.TextField()),
                ('especialista', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='moduloPrincipal.especialista')),
                ('id_cita', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='moduloPrincipal.cita')),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='moduloPrincipal.paciente')),
            ],
        ),
    ]
