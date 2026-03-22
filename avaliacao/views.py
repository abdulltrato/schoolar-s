from django.shortcuts import render
from rest_framework import viewsets
from .models import Avaliacao
from .serializers import AvaliacaoSerializer

# Create your views here.

class AvaliacaoViewSet(viewsets.ModelViewSet):
    queryset = Avaliacao.objects.all()
    serializer_class = AvaliacaoSerializer
