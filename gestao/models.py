import datetime

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from simple_history.models import HistoricalRecords
from adesao.middleware import get_current_user

TIPOS_DILIGENCIA = (
    ('geral', 'Geral'),
    ('componente', 'Específica'),)

LISTA_SITUACAO_ARQUIVO = (
    (0, "Em preenchimento"),
    (1, "Avaliando anexo"),
    (2, "Concluída"),
    (3, "Arquivo aprovado com ressalvas"),
    (4, "Arquivo danificado"),
    (5, "Arquivo incompleto"),
    (6, "Arquivo incorreto"),
)


class Diligencia(models.Model):
    texto_diligencia = models.TextField(max_length=200)
    classificacao_arquivo = models.IntegerField(choices=LISTA_SITUACAO_ARQUIVO,
                                                null=True, blank=True)
    data_criacao = models.DateField(default=datetime.date.today)
    # sistema_cultura = models.ForeignKey('adesao.SistemaCultura', on_delete=models.CASCADE,
                                        # null=True, blank=True)
    componente_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    componente_id = models.PositiveIntegerField()
    componente = GenericForeignKey('componente_type', 'componente_id')
    usuario = models.ForeignKey('adesao.Usuario', on_delete=models.CASCADE)
    tipo_diligencia = models.CharField(
            max_length=10,
            choices=TIPOS_DILIGENCIA)

    def __str__(self):
        return str(self.id)


class ArquivoHistoricalDiligenciaSimples(models.Model):
    arquivo_url = models.URLField(blank=True, null=True)

    class Meta:
        abstract = True


class DiligenciaSimples(models.Model):
    texto_diligencia = models.TextField(max_length=200)
    classificacao_arquivo = models.IntegerField(choices=LISTA_SITUACAO_ARQUIVO, null=True, blank=True)
    data_criacao = models.DateField(default=datetime.date.today)
    usuario = models.ForeignKey('adesao.Usuario', on_delete=models.CASCADE)
    history = HistoricalRecords(bases=[ArquivoHistoricalDiligenciaSimples, ])


class Contato(models.Model):
    contatado = models.CharField(max_length=100)
    contatante = models.ForeignKey("adesao.Usuario", on_delete=models.CASCADE, related_name="contatos")
    data = models.DateField()
    discussao = models.TextField()
    sistema_cultura = models.ForeignKey("adesao.SistemaCultura", on_delete=models.CASCADE, related_name="contatos")

    def save(self, *args, **kwargs):
        self.contatante = get_current_user()
        super().save(*args, **kwargs)
