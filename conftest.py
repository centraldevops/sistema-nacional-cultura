import pytest
import re

from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.urls import reverse

from model_mommy import mommy

from model_mommy.recipe import Recipe

from planotrabalho.models import SituacoesArquivoPlano
from adesao.models import EnteFederado
from adesao.models import Usuario

from snc import settings

@pytest.fixture(scope='function')
def cnpj(requests_mock):
    matcher = re.compile(settings.RECEITA_URL + '\d{14}$')
    requests_mock.get(matcher, json={"status": "OK"})


@pytest.fixture(autouse=True, scope='session')
def situacoes(django_db_setup, django_db_blocker):
    """
    Cria situações dos arquivos do Plano Trabalho enviados no banco de testes
    """
    with django_db_blocker.unblock():

        situacoes = (
            (0, 'Em preenchimento'),
            (1, 'Avaliando anexo'),
            (2, 'Concluída'),
            (3, 'Arquivo aprovado com ressalvas'),
            (4, 'Arquivo danificado'),
            (5, 'Arquivo incompleto'),
            (6, 'Arquivo incorreto'),
        )

        for situacao in situacoes:
            SituacoesArquivoPlano.objects.create(id=situacao[0], descricao=situacao[1])

        yield

        SituacoesArquivoPlano.objects.all().delete()


@pytest.fixture(autouse=True, scope="session")
def ente_federado(django_db_setup, django_db_blocker):

    ufs = {
            11: "RO",
            12: "AC",
            13: "AM",
            14: "RR",
            15: "PA",
            16: "AP",
            17: "TO",
            21: "MA",
            22: "PI",
            23: "CE",
            24: "RN",
            25: "PB",
            26: "PE",
            27: "AL",
            28: "SE",
            29: "BA",
            31: "MG",
            32: "ES",
            33: "RJ",
            35: "SP",
            41: "PR",
            42: "SC",
            43: "RS",
            50: "MS",
            51: "MT",
            52: "GO",
            53: "DF"
            }

    with django_db_blocker.unblock():
        for cod, uf in ufs.items():
            mommy.make("EnteFederado", cod_ibge=cod, nome=uf)

        yield

        EnteFederado.objects.all().delete()


@pytest.fixture(scope='function')
def login(client):
    """
    Cria um usuário fake comum
    """

    User = get_user_model()
    user = User.objects.create(username='teste', email='user@mail.com')
    user.set_password('123456')
    user.save()
    usuario = mommy.make('Usuario', user=user,
                         _fill_optional=['secretario', 'responsavel',
                                         'data_publicacao_acordo'])

    url = reverse("adesao:login")
    response = client.post(url, data={"username": user.username, 
        "password": '123456'})

    yield usuario

    client.logout()
    usuario.secretario.delete()
    usuario.responsavel.delete()
    usuario.delete()
    user.delete()


@pytest.fixture
def login_staff(client):
    """
    Cria um usuário fake com is_staff=True, com permissões de administrador
    """

    User = get_user_model()
    user = User.objects.create(username='staff', is_staff=True,
                               email='staff@mail.com')
    user.set_password('123456')

    user.save()
    usuario = mommy.make('Usuario', user=user)

    login = client.login(username=user.username, password='123456')

    return usuario


@pytest.fixture(scope='function')
def sistema_cultura():

    ente_federado = mommy.make("EnteFederado", cod_ibge=111, _fill_optional=True, nome="Bahia")

    conselho = mommy.make("ConselhoDeCultura", tipo=3, _fill_optional=True)

    conselheiros = mommy.make("Conselheiro", _quantity=3, conselho=conselho, situacao=1, _fill_optional=True)

    sistema_cultura = mommy.make(
            "SistemaCultura",
            estado_processo=6,
            sede__cnpj="28.134.084/0001-75",
            ente_federado=ente_federado,
            conselho=conselho,
            _fill_optional=True
            )

    yield sistema_cultura

    sistema_cultura.delete()

