from django.shortcuts import render
from rest_framework import viewsets
from .models import AreaCurricular, Disciplina, Competencia, CurriculoBase, CurriculoLocal
from .serializers import (
    AreaCurricularSerializer, DisciplinaSerializer, CompetenciaSerializer,
    CurriculoBaseSerializer, CurriculoLocalSerializer
)


class AreaCurricularViewSet(viewsets.ModelViewSet):
    queryset = AreaCurricular.objects.all()
    serializer_class = AreaCurricularSerializer


class DisciplinaViewSet(viewsets.ModelViewSet):
    queryset = Disciplina.objects.all()
    serializer_class = DisciplinaSerializer


class CompetenciaViewSet(viewsets.ModelViewSet):
    queryset = Competencia.objects.all()
    serializer_class = CompetenciaSerializer


class CurriculoBaseViewSet(viewsets.ModelViewSet):
    queryset = CurriculoBase.objects.all()
    serializer_class = CurriculoBaseSerializer


class CurriculoLocalViewSet(viewsets.ModelViewSet):
    queryset = CurriculoLocal.objects.all()
    serializer_class = CurriculoLocalSerializer
