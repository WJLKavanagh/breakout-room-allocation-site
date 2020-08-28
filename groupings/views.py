from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from django.template import RequestContext
from django.http import HttpResponseRedirect

from .models import Allocation
from .forms import UploadFileForm, ManualFileForm

def index(request):
    return render(request, 'groupings/index.html', {"allocations":Allocation.objects.all()})

def query(request, participants, rounds):
    try:
        allocations = Allocation.objects.filter(num_participants=participants, num_rounds__gte=rounds)
    except Allocation.DoesNotExist:
        allocations = None
    
    context = {"participants":participants, "rounds":rounds, "allocations":allocations}
    return render(request, "groupings/query.html", context)

def parse(request, alloc_id):
    return render(request, "groupings/parse.html", {"alloc":Allocation.objects.get(pk=alloc_id), 'upload_form': UploadFileForm(), 'text_input_form': ManualFileForm()})

def download(request, alloc_id):
    # Get the object from the DB
    try:
        db_obj = Allocation.objects.get(id=alloc_id) # Check ID is correct fieldname (by default it should be the right one)
    except Allocation.DoesNotExist:
        return HttpResponse("Unknown matching ID.", content_type='text/plain')
    
    response = HttpResponse(db_obj.download_format, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="allocation.txt"'
    
    return response
    
def parse_upload(request, alloc_id):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_content = request.FILES['upload_file'].read().decode()
            alloc = Allocation.objects.get(pk=alloc_id)
            parsed_allocation = do_allocation_parsing(file_content, alloc)
            response = HttpResponse(parsed_allocation, content_type="text/plain")
            response['Content-Disposition'] = 'attachment; filename="allocation.txt"' 
            return response
        else:
            return HttpResponse('Invalid form submitted:\n'+str(request.FILES['upload_file'].read()), content_type="text/plain")
    else:
        return HttpResponse('Not a Post.', content_type="text/plain")


def parse_text(request, alloc_id):
    if request.method == 'POST':
        form = ManualFileForm(request.POST, request.FILES)
        if form.is_valid():
            print(form['text_content'].value())
            file_content = str(form['text_content'].value())
            alloc = Allocation.objects.get(pk=alloc_id)
            parsed_allocation = do_allocation_parsing(file_content, alloc)
            response = HttpResponse(parsed_allocation, content_type="text/plain")
            response['Content-Disposition'] = 'attachment; filename="allocation.txt"' 
            return response
        else:
            return HttpResponse('Invalid form submitted:\n'+str(request.form['text_content']), content_type="text/plain")
    else:
        return HttpResponse('Not a Post.', content_type="text/plain")


def do_allocation_parsing(emails, allocation_model):
    
    print(emails)
    allocation = eval(allocation_model.matching)

    # Find bounds of id used in allocation. IDs must be contiguous or we're in trouble.
    minid = 100    
    maxid = 0


    for group in allocation[0]:
        group_as_int = [int(x) for x in group]
        if min(group_as_int) < minid:
            minid = min(group_as_int)
        if max(group_as_int) > maxid:
            maxid = max(group_as_int)

    if len(emails.split(", ")) != (maxid - minid) + 1:
        return "Email parsing failed. Expected {0} participants, got {1}".format((maxid-minid)+1, len(emails.split(", ")))

    # Rewrite the allocation with email addresses.
    parsed_allocation = "["

    for round_index in range(len(allocation)):  # every round.
        parsed_allocation += "\n\t[\n"      # start of round.
        for group_index in range(len(allocation[round_index])):     # for group in round
            parsed_allocation += "\t\t["                                # start of group
            for participant_index in range(len(allocation[round_index][group_index])):  # for participant in group
                parsed_allocation += emails.split(", ")[int(allocation[round_index][group_index][participant_index])-minid]     # participant address.
                if participant_index < len(allocation[round_index][group_index]) - 1:
                    parsed_allocation += ", "       # continuation of group.
                else:
                    parsed_allocation += "]"        # end of group    
            if group_index < len(allocation[round_index]) - 1:
                parsed_allocation += ",\n"      # continuation of round
            else:
                parsed_allocation += "\n\t]"      # end of round
        if round_index < len(allocation) - 1:
            parsed_allocation += ",\n"
        else:
            parsed_allocation += "\n]"         # end of allocation    
    return parsed_allocation   


