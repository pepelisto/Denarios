# Generated by Django 4.2.3 on 2023-10-19 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_open_position_sl_order_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='closed_position_sim',
            name='close_method',
        ),
        migrations.AddField(
            model_name='closed_position_sim',
            name='sim_info',
            field=models.CharField(default=None, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='open_position',
            name='sl_order_id',
            field=models.CharField(default=None, max_length=50, null=True),
        ),
    ]
