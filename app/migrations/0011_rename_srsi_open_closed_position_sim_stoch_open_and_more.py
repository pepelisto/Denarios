# Generated by Django 4.2.3 on 2023-09-17 17:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_rename_atr_closed_position_sim_sl_low_limit_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='closed_position_sim',
            old_name='srsi_open',
            new_name='stoch_open',
        ),
        migrations.RenameField(
            model_name='open_position_sim',
            old_name='srsi',
            new_name='stoch',
        ),
    ]
