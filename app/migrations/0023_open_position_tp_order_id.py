# Generated by Django 4.2.3 on 2023-10-30 22:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0022_closed_position_sim_close_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='open_position',
            name='tp_order_id',
            field=models.CharField(default=None, max_length=50, null=True),
        ),
    ]
