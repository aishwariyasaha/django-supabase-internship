from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .forms import DataEntryForm

def home(request):
    form = DataEntryForm()
    return render(request, 'home.html', {
        'form': form,
        'entries': [],
        'metabase_url': "",
        'supabase_connected': False
    })

@csrf_exempt
def add_entry(request):
    if request.method == 'POST':
        form = DataEntryForm(request.POST)
        if form.is_valid():
            form.save()
    return redirect('home')