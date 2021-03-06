from django import forms
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.crypto import get_random_string
from django.forms import ModelForm
from django.template.defaultfilters import filesizeformat
from django.forms import formset_factory

from dal import autocomplete
from localflavor.br.forms import BRCPFField

from snc.forms import RestrictedFileField, BRCNPJField

from .models import Usuario, Municipio, Responsavel, Uf
from .models import Secretario, Funcionario, SistemaCultura, Sede, Gestor

from snc.widgets import FileUploadWidget
from .utils import limpar_mascara
import re

from adesao.models import SolicitacaoDeTrocaDeCadastrador, SolicitacaoDeAdesao

content_types = [
    'image/png',
    'image/jpg',
    'image/jpeg',
    'application/pdf',
    'application/msword',
    'application/vnd.oasis.opendocument.text',
    'application/vnd.openxmlformats-officedocument.' +
    'wordprocessingml.document',
    'application/x-rar-compressed',
    'application/zip',
    'application/octet-stream',
    'text/plain']

content_types_solicitacao = [
    'image/png',
    'image/jpg',
    'image/jpeg',
    'application/pdf',]

class CadastrarUsuarioForm(UserCreationForm):
    username = BRCPFField()
    confirmar_email = forms.EmailField(required=True)
    email = forms.EmailField(required=True)
    email_pessoal = forms.EmailField(required=False)
    confirmar_email_pessoal = forms.EmailField(required=False)
    nome_usuario = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    def clean_confirmar_email(self):
        if self.data.get('email') != self.cleaned_data['confirmar_email']:
            raise forms.ValidationError(
                'Confirmação de e-mail não confere.')

        return self.cleaned_data['confirmar_email']

    def clean_confirmar_email_pessoal(self):
        if self.cleaned_data.get('email_pessoal', None):
            if self.data.get('email_pessoal') != self.cleaned_data['confirmar_email_pessoal']:
                raise forms.ValidationError(
                    'Confirmação de e-mail pessoal não confere.')

            return self.cleaned_data['confirmar_email_pessoal']

    def clean_email(self):
        usuarios = Usuario.objects.filter(
            Q(user__email=self.cleaned_data['email']) |
            Q(email_pessoal=self.cleaned_data['email']))

        if not usuarios:
            return self.cleaned_data['email']
        else:
            raise forms.ValidationError('Este e-mail já foi cadastrado!')

    def clean_email_pessoal(self):
        if self.cleaned_data.get('email_pessoal', None):
            usuarios = Usuario.objects.filter(
                Q(user__email=self.cleaned_data['email_pessoal']) |
                Q(email_pessoal=self.cleaned_data['email_pessoal']))
            if not usuarios:
                return self.cleaned_data['email_pessoal']
            else:
                raise forms.ValidationError('Este e-mail já foi cadastrado!')

    def clean_username(self):
        try:
            User.objects.get(username=''.join(re.findall(
                '\d+',
                self.cleaned_data['username'])))
            raise forms.ValidationError('Esse CPF já foi cadastrado.')
        except User.DoesNotExist:
            return self.cleaned_data['username']

        return self.cleaned_data['username']

    def save(self, commit=True):
        user = super(CadastrarUsuarioForm, self).save(commit=False)
        user.username = limpar_mascara(self.cleaned_data['username'])
        user.email = self.cleaned_data['email']
        user.is_active = False
        if commit:
            user.save()

        usuario = Usuario()
        usuario.user = user
        usuario.nome_usuario = self.cleaned_data['nome_usuario']
        usuario.email_pessoal = self.cleaned_data['email_pessoal']
        codigo_ativacao = get_random_string()
        usuario.codigo_ativacao = codigo_ativacao
        if commit:
            usuario.save()

        return user


class CadastrarGestor(ModelForm):
    cpf = BRCPFField()
    termo_posse = RestrictedFileField(content_types=content_types, max_upload_size=52428800)
    rg_copia = RestrictedFileField(content_types=content_types, max_upload_size=52428800)
    cpf_copia = RestrictedFileField(content_types=content_types, max_upload_size=52428800)

    def __init__(self, *args, **kwargs):
        logged_user = kwargs.pop('logged_user')
        super(CadastrarGestor, self).__init__(*args, **kwargs)

        if logged_user.is_staff:
            self.fields['rg_copia'].widget = FileUploadWidget(attrs={
                'label': 'Cópia do RG'
            })
            self.fields['cpf_copia'].widget = FileUploadWidget(attrs={
                'label': 'Cópia do CPF'
            })
            self.fields['termo_posse'].widget = FileUploadWidget(attrs={
                'label': 'Cópia do Termo de Posse'
            })

    def clean_estado_expeditor(self):
        return Uf.objects.get(codigo_ibge=int(self.cleaned_data['estado_expeditor']))

    class Meta:
        model = Gestor
        exclude = ('tipo_funcionario', 'estado_endereco',)


class CadastrarSede(ModelForm):
    # cnpj = BRCNPJField()

    class Meta:
        model = Sede
        fields = '__all__'


class CadastrarSistemaCulturaForm(ModelForm, forms.Form):

    def clean(self):
        super(CadastrarSistemaCulturaForm, self).clean()

        if 'ente_federado' in self.changed_data:
            sistema_cultura = SistemaCultura.sistema.filter(
                ente_federado=self.cleaned_data['ente_federado'])
            '''
            if sistema_cultura:
                self.add_error(
                    'ente_federado', 'Este ente federado já foi cadastrado!')
            '''
        
        """ for form in forms:
            name = form.cleaned_data['name'].upper()
            form.cleaned_data['name'] = name
            # update the instance value.
            form.instance.name = name
 """
    class Meta:
        model = SistemaCultura
        fields = ('ente_federado', 'conferencia_nacional')
        widgets = {
            'ente_federado': autocomplete.ModelSelect2(url='gestao:ente_chain')}

class TrocarCadastradorForm(ModelForm):
    oficio = RestrictedFileField(content_types=content_types_solicitacao, max_upload_size=52428800)

    class Meta:
        model = SolicitacaoDeTrocaDeCadastrador
        fields = ('ente_federado',)
        widgets = {
            'ente_federado': autocomplete.ModelSelect2(url='gestao:ente_chain')}

class SolicitacaoDeAdesaoForm(ModelForm):
    oficio = RestrictedFileField(content_types=content_types_solicitacao, max_upload_size=52428800)
    class Meta:
        model = SolicitacaoDeAdesao
        fields = ('oficio',)

class CadastrarFuncionarioForm(ModelForm):
    cpf = BRCPFField()

    rg  = forms.CharField(required=True)
    orgao_expeditor_rg = forms.CharField(required=True)
   # estado_expeditor = forms.CharField(required=True)
    nome = forms.CharField(required=True)
    cargo = forms.CharField(required=True)
    instituicao = forms.CharField(required=True)
    telefone_um = forms.CharField(required=True)
    email_institucional = forms.EmailField(required=True)
    email_pessoal = forms.EmailField(required=False)
    endereco = forms.CharField(required=True)
    complemento = forms.CharField(required=False)
    cep = forms.CharField(required=True)
    bairro = forms.CharField(required=True)

    def clean_estado_endereco(self):
        return Uf.objects.get(codigo_ibge=int(self.cleaned_data['estado_endereco']))

    def clean_estado_expeditor(self):
        return Uf.objects.get(codigo_ibge=int(self.cleaned_data['estado_expeditor']))

    class Meta:
        model = Funcionario
        exclude = ('tipo_funcionario',)

'''
class TrocaCadastradorForm(ModelForm):

    class Meta:
        model = RequerimentoTrocaCadastrador
        fields = ('ente_federado', 'oficio')
        widgets = {
            'ente_federado': autocomplete.ModelSelect2(url='gestao:ente_chain')}
'''