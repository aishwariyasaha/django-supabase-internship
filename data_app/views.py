from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from .models import DataEntry
from .forms import DataEntryForm

# Check if we're on Render
IS_RENDER = 'RENDER' in os.environ

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
            # Save to Django database
            entry = form.save()
            
            # Only attempt Supabase sync if not on Render
            if not IS_RENDER:
                try:
                    sync_to_supabase(entry)
                except:
                    pass  # Silently fail on deployment
            
            return redirect('home')
    
    return redirect('home')

def sync_to_supabase(entry):
    """Sync data to Supabase - only called locally"""
    if not IS_RENDER:
        try:
            from supabase import create_client
            from dotenv import load_dotenv
            from pathlib import Path
            import os
            
            # Load env only locally
            BASE_DIR = Path(__file__).resolve().parent.parent
            env_path = BASE_DIR / '.env'
            load_dotenv(env_path)
            
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_ANON_KEY')
            
            if supabase_url and supabase_key:
                supabase = create_client(supabase_url, supabase_key)
                data = {
                    'name': entry.name,
                    'email': entry.email,
                    'age': entry.age,
                    'salary': float(entry.salary),
                    'department': entry.department,
                    'django_id': entry.id,
                    'date_created': entry.date_created.isoformat()
                }
                supabase.table('data_entries').insert(data).execute()
        except:
            pass  # Fail silently on deployment