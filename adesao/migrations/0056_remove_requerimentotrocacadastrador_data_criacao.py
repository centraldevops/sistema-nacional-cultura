# Generated by Django 2.0.8 on 2020-07-12 16:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('adesao', '0055_requerimentotrocacadastrador'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='requerimentotrocacadastrador',
            name='data_criacao',
        ),
    ]
