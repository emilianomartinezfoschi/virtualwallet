# Generated by Django 5.0.3 on 2024-04-24 14:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app_billetera", "0005_remove_historial_date_of_change"),
    ]

    operations = [
        migrations.RenameField(
            model_name="historial",
            old_name="destiny",
            new_name="destino_del_dinero",
        ),
    ]
