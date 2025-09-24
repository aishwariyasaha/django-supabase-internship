from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import DataEntry
from .forms import DataEntryForm

def home(request):
    try:
        form = DataEntryForm()
        entries = DataEntry.objects.all().order_by('-date_created')
        
        return render(request, 'home.html', {
            'form': form,
            'entries': entries,
            'metabase_url': "",
            'supabase_connected': False
        })
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")

@csrf_exempt
def add_entry(request):
    if request.method == 'POST':
        try:
            form = DataEntryForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('home')
        except Exception as e:
            print(f"Form error: {e}")
    return redirect('home')