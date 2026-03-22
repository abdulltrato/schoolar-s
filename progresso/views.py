from django.shortcuts import render
from rest_framework import viewsets
from .models import Progressao
from .serializers import ProgressaoSerializer

# Create your views here.

class ProgressaoViewSet(viewsets.ModelViewSet):
    queryset = Progressao.objects.all()
    serializer_class = ProgressaoSerializer
