# Generated by Django 2.0.8 on 2020-07-08 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planotrabalho', '0043_auto_20200708_1029'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalorgaogestor2',
            name='comprovante_cnpj_orgao',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='orgaogestor2',
            name='comprovante_cnpj_orgao',
            field=models.FileField(blank=True, null=True, upload_to='media/'),
        ),
    ]