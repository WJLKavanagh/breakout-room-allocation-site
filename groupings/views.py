from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
from .models import Allocation

def index(request):
    return render(request, 'groupings/index.html', None)


def query(request, participants, rounds):
    context = {"participants":participants, "rounds":rounds}
    return render(request, "groupings/query.html", context)