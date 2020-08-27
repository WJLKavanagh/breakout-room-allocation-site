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

def parse(request, alloc_id):
    return render(request, "groupings/parse.html", {"alloc":Allocation.objects.get(pk=alloc_id)})

def download(request, alloc_id):
    # Get the object from the DB
    try:
        db_obj = Allocation.objects.get(id=alloc_id) # Check ID is correct fieldname (by default it should be the right one)
    except Allocation.DoesNotExist:
        return HttpResponse("Unknown matching ID.", content_type='text/plain')
    
    response = HttpResponse(db_obj.matching, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="match.txt"'
    
    return response
    