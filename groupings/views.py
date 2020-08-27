from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
from .models import Allocation

def index(request):
    return render(request, 'groupings/index.html', {"allocations":Allocation.objects.all()})


def query(request, participants, rounds):
    try:
        allocations = Allocation.objects.filter(num_participants=participants, num_rounds=rounds)
    except Allocation.DoesNotExist:
        allocations = None
    context = {"participants":participants, "rounds":rounds, "allocations":allocations}
    return render(request, "groupings/query.html", context)

def allocation(request, alloc):
    return render(request, "groupings/allocation.html", None)
