# Generated by Django 5.0.3 on 2024-03-31 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0005_alter_room_cost_per_day'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='number',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]