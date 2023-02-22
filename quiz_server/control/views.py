from django.shortcuts import render
from .models import *

# Create your views here.
def index(request):
    context = {
        "questions" : Question.objects.filter(game__is_active=True).all()
    }
    return render(request, 'control/index.html', context)