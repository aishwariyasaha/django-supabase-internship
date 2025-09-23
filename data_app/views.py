from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from .models import DataEntry
from .forms import DataEntryForm

def home(request):
    form = DataEntryForm()
    entries = DataEntry.objects.all().order_by('-date_created')
    
    return render(request, 'home.html', {
        'form': form,
        'entries': entries,
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
    return redirect('home')

# Remove the sync_to_supabase function completely for deployment