from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count

from rest_framework import filters
from rest_framework import generics
from rest_framework.response import Response

from adesao.models import SistemaCultura
from adesao.models import EnteFederado
from planotrabalho.models import PlanoTrabalho

# from .serializers import MunicipioSerializer as SistemaCulturaSerializer
from .serializers import SistemaCulturaSerializer
from .serializers import SistemaCulturaDetailSerializer
from .serializers import PlanoTrabalhoSerializer

from .filters import SistemaCulturaFilter
from .filters import PlanoTrabalhoFilter

from .metadata import MunicipioMetadata as SistemaCulturaMetadata
from .metadata import PlanoTrabalhoMetadata


def swagger_index(request):
    return render(request, 'swagger/index.html')


class SistemaCulturaAPIList(generics.ListAPIView):
    queryset = SistemaCultura.sistema.all()
    serializer_class = SistemaCulturaSerializer
    metadata_class = SistemaCulturaMetadata

    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_class = SistemaCulturaFilter
    ordering_fields = ('ente_federado__nome', 'ente_federado')

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        municipios = queryset.filter(ente_federado__cod_ibge__gt=100)
        estados = queryset.filter(ente_federado__cod_ibge__lte=100)

        response = super().list(self, request)
        response.data['municipios'] = municipios.count()
        response.data['municipios_aderidos'] = municipios.filter(estado_processo=6).count()
        response.data['estados'] = estados.count()
        response.data['estados_aderidos'] = estados.filter(estado_processo=6).count()

        return response


class SistemaCulturaDetail(generics.RetrieveAPIView):
    queryset = SistemaCultura.sistema.filter()
    serializer_class = SistemaCulturaSerializer


class PlanoTrabalhoList(generics.ListAPIView):
    queryset = SistemaCultura.sistema.all()
    serializer_class = PlanoTrabalhoSerializer
    metadata_class = PlanoTrabalhoMetadata

    filter_backends = (DjangoFilterBackend,)
    filterset_class = PlanoTrabalhoFilter


class PlanoTrabalhoDetail(generics.RetrieveAPIView):
    queryset = SistemaCultura.sistema.filter()
    serializer_class = SistemaCulturaDetailSerializer
