# Generated by Django 2.0.8 on 2019-03-25 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adesao', '0037_merge_20190320_1154'),
    ]

    operations = [
        migrations.AddField(
            model_name='sistemacultura',
            name='data_publicacao_retificacao',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sistemacultura',
            name='link_publicacao_retificacao',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        
    ]