# Generated by Django 2.0.8 on 2019-07-30 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adesao', '0046_auto_20190729_1932'),
    ]

    operations = [
        migrations.AddField(
            model_name='sistemacultura',
            name='oficio_prorrogacao_prazo',
            field=models.FileField(blank=True, max_length=255, null=True, upload_to='oficio_prorrogacao_prazo'),
        ),
    ]
