from django.shortcuts import render
from rest_framework import viewsets
from .models import Relatorio
from .serializers import RelatorioSerializer

# Create your views here.

class RelatorioViewSet(viewsets.ModelViewSet):
    queryset = Relatorio.objects.all()
    serializer_class = RelatorioSerializer
