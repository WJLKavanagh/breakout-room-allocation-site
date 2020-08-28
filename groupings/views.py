from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from django.template import RequestContext
from django.http import HttpResponseRedirect

from .models import Allocation
from .forms import UploadFileForm

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
    return render(request, "groupings/parse.html", {"alloc":Allocation.objects.get(pk=alloc_id), 'upload_form': UploadFileForm()})

def download(request, alloc_id):
    # Get the object from the DB
    try:
        db_obj = Allocation.objects.get(id=alloc_id) # Check ID is correct fieldname (by default it should be the right one)
    except Allocation.DoesNotExist:
        return HttpResponse("Unknown matching ID.", content_type='text/plain')
    
    response = HttpResponse(db_obj.matching, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="allocation.txt"'
    
    return response
    
# def upload_file(request):
#     if request.method == 'POST':
#         form = UploadFileForm(request.POST, request.FILES)
#         if form.is_valid():
#             handle_uploaded_file(request.FILES['file'])
#             return HttpResponse('that worked.', content_type="text/plain")
#     else:
#         form = UploadFileForm()
#     return render(request, 'upload.html', {'form': form})

# def handle_uploaded_file(f):
#     with open('some/file/name.txt', 'wb+') as destination:
#         for chunk in f.chunks():
#             destination.write(chunk)

def parse_upload(request, alloc_id):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_content = request.FILES['upload_file'].read().decode()
            alloc = Allocation.objects.get(pk=alloc_id)
            parsed_allocation = do_allocation_parsing(file_content, alloc)
            return HttpResponse(parsed_allocation, content_type="text/plain")
        else:
            return HttpResponse('Invalid form submitted:\n'+str(request.FILES['upload_file'].read()), content_type="text/plain")
    else:
        return HttpResponse('Not a Post.', content_type="text/plain")


def do_allocation_parsing(emails, allocation_model):
    
    allocation = eval(allocation_model.matching)


    # Find bounds of id used in allocation. IDs must be contiguous or we're in trouble.
    minid = 100    
    maxid = 0
    for group in allocation[0]:
        print(group)
        group_as_int = [int(x) for x in group]
        if min(group_as_int) < minid:
            minid = min(group_as_int)
        if max(group_as_int) > maxid:
            maxid = max(group_as_int)

    if len(emails) != (maxid - minid) + 1:
        return "Email parsing failed. Expected {0} participants, got {1}".format((maxid-minid)+1, len(emails))

    # Rewrite the allocation with email addresses.
    parsed_allocation = "["
    for rou in allocation:              # for every round
        parsed_allocation += "["
        for group in rou:
            parsed_allocation += "["
            for id in group:
                parsed_allocation += emails[int(id)-minid]
                parsed_allocation += ", "
            parsed_allocation += "],"
        parsed_allocation += "],\n"
    return parsed_allocation + "]"