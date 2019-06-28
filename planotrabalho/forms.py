import datetime
from django import forms
from django.forms import ModelForm
from django.forms.widgets import FileInput

from snc.forms import RestrictedFileField, BRCNPJField

from .models import CriacaoSistema, OrgaoGestor, ConselhoCultural
from .models import FundoCultura, Componente
from .models import FundoDeCultura, PlanoCultura, ConselhoDeCultura
from .models import Conselheiro, SITUACAO_CONSELHEIRO
from .models import LISTA_PERFIS_ORGAO_GESTOR
from .models import ArquivoComponente2
from .models import OrgaoGestor2
from .utils import add_anos
from adesao.models import SistemaCultura
from gestao.forms import content_types

from snc.widgets import FileUploadWidget


SETORIAIS = (
    ('0', '-- Selecione um Segmento --'),
    ('1', 'Arquitetura e Urbanismo'),
    ('2', 'Arquivos'),
    ('3', 'Arte Digital'),
    ('4', 'Artes Visuais'),
    ('5', 'Artesanato'),
    ('6', 'Audiovisual'),
    ('7', 'Circo'),
    ('8', 'Culturas Afro-brasileiras'),
    ('9', 'Culturas dos Povos Indígenas'),
    ('10', 'Culturas Populares'),
    ('11', 'Dança'),
    ('12', 'Design'),
    ('13', 'Literatura, Livro e Leitura'),
    ('14', 'Moda'),
    ('15', 'Museus'),
    ('16', 'Música Erudita'),
    ('17', 'Música Popular'),
    ('18', 'Patrimônio Imaterial'),
    ('19', 'Patrimônio Material'),
    ('20', 'Teatro'),
    ('21', 'Outros')
    )


class CriarComponenteForm(ModelForm):
    componentes = {
            "legislacao": 0,
            "orgao_gestor": 1,
            "fundo_cultura": 2,
            "conselho": 3,
            "plano": 4,
    }

    arquivo = forms.FileField(required=True, widget=FileInput)
    data_publicacao = forms.DateField(required=True)

    def __init__(self, *args, **kwargs):
        self.sistema = kwargs.pop('sistema')
        self.tipo_componente = kwargs.pop('tipo')
        logged_user = kwargs.pop('logged_user')
        super(CriarComponenteForm, self).__init__(*args, **kwargs)

        if logged_user.is_staff:
            self.fields['arquivo'].widget = FileUploadWidget(attrs={
                'label': 'Componente'
            })

    def save(self, commit=True, *args, **kwargs):
        componente = super(CriarComponenteForm, self).save(commit=False)
        if 'arquivo' in self.changed_data:
            componente.situacao = 1

        if commit:
            componente.tipo = self.componentes.get(self.tipo_componente)
            componente.data_publicacao = self.cleaned_data['data_publicacao']
            componente.arquivo = None
            componente.save()
            sistema_cultura = getattr(componente, self.tipo_componente)
            sistema_cultura.add(self.sistema)
            componente.arquivo = self.cleaned_data['arquivo']
            componente.save()
            setattr(self.sistema, self.tipo_componente, componente)
            self.sistema.save()

        return componente

    class Meta:
        model = Componente
        fields = ('arquivo', 'data_publicacao')


class CriarOrgaoGestorForm(CriarComponenteForm):
    perfil = forms.ChoiceField(required=True, choices=LISTA_PERFIS_ORGAO_GESTOR)

    def __init__(self, *args, **kwargs):
        logged_user = kwargs['logged_user']
        super(CriarOrgaoGestorForm, self).__init__(*args, **kwargs)

        if logged_user.is_staff:
            self.fields['arquivo'].widget = FileUploadWidget(attrs={
                'label': 'Órgão Gestor'
            })

    class Meta:
        model = OrgaoGestor2
        fields = ('perfil', 'arquivo', 'data_publicacao',)


class CriarFundoForm(CriarComponenteForm):
    cnpj = BRCNPJField(required=False)
    comprovante = forms.FileField(required=False, widget=FileInput)
    arquivo = forms.FileField(required=False, widget=FileInput)
    data_publicacao = forms.DateField(required=False)
    mesma_lei = forms.NullBooleanField(required=False, widget=forms.RadioSelect(choices=[(True, 'Sim'),
                                                            (False, 'Não')]))
    possui_cnpj = forms.NullBooleanField(required=False, widget=forms.RadioSelect(choices=[(True, 'Sim'),
                                                            (False, 'Não')]))

    def __init__(self, *args, **kwargs):
        logged_user = kwargs['logged_user']
        super(CriarFundoForm, self).__init__(*args, **kwargs)

        if logged_user.is_staff:
            self.fields['arquivo'].widget = FileUploadWidget(attrs={
                'label': 'Anexo da Lei'
            })
            self.fields['comprovante'].widget = FileUploadWidget(attrs={
                'label': 'Comprovante do CNPJ'
            })

    def clean_possui_cnpj(self):
        if self.data.get('possui_cnpj', None) is None:
            raise forms.ValidationError("Este campo é obrigatório")

        return self.cleaned_data['possui_cnpj']

    def clean_arquivo(self):
        if self.data.get('mesma_lei', None) == 'False' and not self.cleaned_data['arquivo']:
            raise forms.ValidationError("Este campo é obrigatório")

        return self.cleaned_data['arquivo']

    def clean_data_publicacao(self):
        if self.data.get('mesma_lei', None) == 'False' and not self.cleaned_data['data_publicacao']:
            raise forms.ValidationError("Este campo é obrigatório")

        return self.cleaned_data['data_publicacao']

    def clean_mesma_lei(self):
        if self.data.get('mesma_lei', None) == 'True':
            try:
                if self.sistema.legislacao.arquivo.url:
                    return self.cleaned_data['mesma_lei']
            except (ValueError, AttributeError) as e:
                raise forms.ValidationError("Você não possui a lei do sistema cadastrada")
        elif self.data.get('mesma_lei', None) is None:
            raise forms.ValidationError("Este campo é obrigatório")

    def clean_cnpj(self):
        if self.data.get('possui_cnpj', None) == 'True' and not self.cleaned_data['cnpj']:
            raise forms.ValidationError("Este campo é obrigatório")
        elif self.data.get('possui_cnpj', None) == 'False' and self.cleaned_data['cnpj']:
            self.cleaned_data['cnpj'] = None

        return self.cleaned_data['cnpj']

    def clean_comprovante(self):
        if self.data.get('possui_cnpj', None) == 'True' and not self.cleaned_data['comprovante']:
            raise forms.ValidationError("Este campo é obrigatório")
        elif self.data.get('possui_cnpj', None) == 'False' and self.cleaned_data['comprovante']:
            self.cleaned_data['comprovante'] = None

        return self.cleaned_data['comprovante']


    def save(self, commit=True, *args, **kwargs):
        componente = super(CriarComponenteForm, self).save(commit=False)
        componente.tipo = self.componentes.get(self.tipo_componente)

        if 'arquivo' in self.changed_data:
            componente.situacao = 1
            componente.arquivo = None
            componente.save()

        if self.cleaned_data['mesma_lei']:
            componente.arquivo = self.sistema.legislacao.arquivo
            componente.situacao = self.sistema.legislacao.situacao
            componente.data_publicacao = self.sistema.legislacao.data_publicacao
        else:
            componente.arquivo = self.cleaned_data['arquivo']
            componente.data_publicacao = self.cleaned_data['data_publicacao']

        componente.cnpj = self.cleaned_data['cnpj']
        componente.save()

        if self.cleaned_data['possui_cnpj']:
            if 'comprovante' in self.changed_data:
                componente.comprovante_cnpj = ArquivoComponente2()
                componente.comprovante_cnpj.situacao = 1
                componente.comprovante_cnpj.save()
                componente.comprovante_cnpj.comprovantes.add(componente)
                componente.comprovante_cnpj.arquivo = self.cleaned_data['comprovante']
                componente.comprovante_cnpj.save()
        else:
            componente.comprovante_cnpj = None
            componente.save()

        sistema_cultura = getattr(componente, self.tipo_componente)
        sistema_cultura.add(self.sistema)

    class Meta:
        model = FundoDeCultura
        fields = ('cnpj', 'arquivo', 'data_publicacao')


class CriarConselhoForm(ModelForm):
    arquivo_lei = forms.FileField(required=False, widget=FileInput, label="Arquivo da Lei")
    data_publicacao_lei = forms.DateField(required=False, label="Data de publicação da Lei")
    arquivo = forms.FileField(required=False, widget=FileInput, label="Arquivo da Lei")
    mesma_lei = forms.NullBooleanField(required=False, widget=forms.RadioSelect(choices=[(True, 'Sim'),
                                                            (False, 'Não')]), label="Lei é a mesma do sistema")
    possui_ata = forms.NullBooleanField(required=False, widget=forms.RadioSelect(choices=[(True, 'Sim'),
                                                            (False, 'Não')]))
    exclusivo_cultura = forms.NullBooleanField(required=False, widget=forms.RadioSelect(choices=[(True, 'Sim'),
                                                            (False, 'Não')]))
    paritario = forms.NullBooleanField(required=False, widget=forms.RadioSelect(choices=[(True, 'Sim'),
                                                            (False, 'Não')]), label="Paritário")
    def __init__(self, *args, **kwargs):
        self.sistema = kwargs.pop('sistema')
        self.tipo_componente = kwargs.pop('tipo')
        logged_user = kwargs.pop('logged_user')

        super(CriarConselhoForm, self).__init__(*args, **kwargs)

        if logged_user.is_staff:
            self.fields['arquivo'].widget = FileUploadWidget(attrs={
                'label': 'Arquivo da ata da última reunião'
            })
            self.fields['arquivo_lei'].widget = FileUploadWidget(attrs={
                'label': 'Lei do Conselho de Cultura'
            })

    def clean_paritario(self):
        if self.cleaned_data['paritario'] is None:
            raise forms.ValidationError("Este campo é obrigatório")

        return self.cleaned_data['paritario']

    def clean_possui_ata(self):
        if self.data.get('possui_ata', None) is None:
            raise forms.ValidationError("Este campo é obrigatório")

        return self.cleaned_data['possui_ata']

    def clean_exclusivo_cultura(self):
        if self.cleaned_data['exclusivo_cultura'] is None:
            raise forms.ValidationError("Este campo é obrigatório")

        return self.cleaned_data['exclusivo_cultura']

    def clean_arquivo_lei(self):
        if self.data.get('mesma_lei', None) == 'False' and not self.cleaned_data['arquivo_lei']:
            raise forms.ValidationError("Este campo é obrigatório")

        return self.cleaned_data['arquivo_lei']

    def clean_data_publicacao_lei(self):
        if self.data.get('mesma_lei', None) == 'False' and not self.cleaned_data['data_publicacao_lei']:
            raise forms.ValidationError("Este campo é obrigatório")

        return self.cleaned_data['data_publicacao_lei']

    def clean_mesma_lei(self):
        if self.data.get('mesma_lei', None) == 'True':
            try:
                if self.sistema.legislacao.arquivo.url:
                    return self.cleaned_data['mesma_lei']
            except (ValueError, AttributeError) as e:
                raise forms.ValidationError("Você não possui a lei do sistema cadastrada")
        elif self.data.get('mesma_lei', None) is None:
            raise forms.ValidationError("Este campo é obrigatório")

    def clean_arquivo(self):
        if self.data.get('possui_ata', None) == 'True' and not self.cleaned_data['arquivo']:
            raise forms.ValidationError("Este campo é obrigatório")
        elif self.data.get('possui_ata', None) == 'False':
            self.cleaned_data['arquivo'] = None

        return self.cleaned_data['arquivo']

    def clean_data_publicacao(self):
        if self.data.get('possui_ata', None) == 'True' and not self.cleaned_data['data_publicacao']:
            raise forms.ValidationError("Este campo é obrigatório")
        elif self.data.get('possui_ata', None) == 'False':
            self.cleaned_data['data_publicacao'] = None

        return self.cleaned_data['data_publicacao']

    def save(self, commit=True, *args, **kwargs):
        conselho = super(CriarConselhoForm, self).save(commit=False)
        conselho.tipo = 3

        if 'arquivo' in self.changed_data:
            conselho.situacao = 1
            conselho.arquivo = None
            conselho.save()

        conselho.arquivo = self.cleaned_data['arquivo']
        conselho.data_publicacao = self.cleaned_data['data_publicacao']
        conselho.save()

        if 'mesma_lei' in self.changed_data or 'arquivo_lei' in self.changed_data:
            conselho.lei = ArquivoComponente2()
            conselho.lei.save()
            conselho.lei.conselhos.add(conselho)

            if self.cleaned_data['mesma_lei']:
                conselho.lei.arquivo = self.sistema.legislacao.arquivo
                conselho.lei.situacao = self.sistema.legislacao.situacao
                conselho.lei.data_publicacao = self.sistema.legislacao.data_publicacao
            else:
                conselho.lei.situacao = 1
                conselho.lei.arquivo = self.cleaned_data['arquivo_lei']
                conselho.lei.data_publicacao = self.cleaned_data['data_publicacao_lei']

            conselho.lei.save()

        sistema_cultura = conselho.conselho
        sistema_cultura.add(self.sistema)

    class Meta:
        model = ConselhoDeCultura
        fields = ('arquivo', 'data_publicacao', 'paritario', 'exclusivo_cultura',)


class CriarConselheiroForm(ModelForm):
    segmento = forms.ChoiceField(choices=SETORIAIS)
    outros = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        self.conselho_id = kwargs.pop('conselho')
        super(CriarConselheiroForm, self).__init__(*args, **kwargs)

    def clean_segmento(self):
        if self.cleaned_data['segmento'] == '0':
            raise forms.ValidationError("Este campo é obrigatório.")

        return self.cleaned_data['segmento']

    def clean(self):
        if self.cleaned_data['segmento'] == '21' and self.cleaned_data['outros'] == '':
            self.add_error('segmento', 'Este campo é obrigatório.')

    def save(self, commit=True, *args, **kwargs):
        conselheiro = super(CriarConselheiroForm, self).save(commit=False)
        conselho = Componente.objects.get(id=self.conselho_id)
        conselheiro.conselho = conselho.conselhodecultura
        conselheiro.data_cadastro = datetime.datetime.now()
        conselheiro.data_situacao = datetime.datetime.now()
        conselheiro.situacao = 1  # Situação 1 = Habilitado

        if self.cleaned_data['segmento'] == '21':  # outros
            outros = self.cleaned_data['outros']  # texto livre
            conselheiro.segmento = outros if outros else 'Outros'
        else:
            segmento = self.cleaned_data['segmento']
            conselheiro.segmento = dict(SETORIAIS).get(segmento)

        if commit:
            conselheiro.save()
        return conselheiro

    class Meta:
        model = Conselheiro
        exclude = ['conselho']


class AlterarConselheiroForm(ModelForm):
    segmento = forms.ChoiceField(choices=SETORIAIS)
    outros = forms.CharField(required=False)
    situacao = forms.ChoiceField(choices=SITUACAO_CONSELHEIRO, required=True)

    def __init__(self, *args, **kwargs):
        super(AlterarConselheiroForm, self).__init__(*args, **kwargs)
        self.fields['situacao'].required = False

    def clean_segmento(self):
        if self.cleaned_data['segmento'] == '0':
            raise forms.ValidationError("Este campo é obrigatório.")

        return self.cleaned_data['segmento']

    def clean(self):
        if self.cleaned_data['segmento'] == '21' and self.cleaned_data['outros'] == '':
            self.add_error('segmento', 'Este campo é obrigatório.')

    def save(self, commit=True, *args, **kwargs):
        conselheiro = super(AlterarConselheiroForm, self).save(commit=False)

        if self.cleaned_data['segmento'] == '21':  # outros
            outros = self.cleaned_data['outros']  # texto livre
            conselheiro.segmento = outros if outros else 'Outros'
        else:
            segmento = self.cleaned_data['segmento']
            conselheiro.segmento = dict(SETORIAIS).get(segmento)

        if commit:
            conselheiro.save()
        return conselheiro

    class Meta:
        model = Conselheiro
        exclude = ['conselho', 'situacao']


class DesabilitarConselheiroForm(ModelForm):

    def save(self, commit=True, *args, **kwargs):
        conselheiro = super(DesabilitarConselheiroForm, self).save(commit=False)

        conselheiro.data_situacao = datetime.datetime.now()
        conselheiro.situacao = 0  # Situação 0 = Desabilitado

        if commit:
            conselheiro.save()
        return conselheiro

    class Meta:
        model = Conselheiro
        fields = ['situacao', 'data_situacao']
