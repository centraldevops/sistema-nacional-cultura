# Generated by Django 2.0.8 on 2020-07-08 13:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planotrabalho', '0042_auto_20200708_1006'),
    ]

    operations = [
        migrations.RenameField(
            model_name='historicalorgaogestor2',
            old_name='comprovante',
            new_name='comprovante_cnpj',
        ),
        migrations.RenameField(
            model_name='orgaogestor2',
            old_name='comprovante',
            new_name='comprovante_cnpj',
        ),
    ]
