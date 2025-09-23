from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from .models import DataEntry
from .forms import DataEntryForm

# Load environment variables from project root
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / '.env'
load_dotenv(env_path)

# Initialize Supabase client only if variables exist AND not on Render
supabase = None
if 'RENDER' not in os.environ:  # Only enable Supabase locally, not on deployment
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')

    if supabase_url and supabase_key:
        try:
            from supabase import create_client, Client
            supabase: Client = create_client(supabase_url, supabase_key)
            print("✅ Supabase client initialized successfully")
        except Exception as e:
            print(f"❌ Supabase initialization error: {e}")
            supabase = None
    else:
        print("⚠️ Supabase credentials not found - running in local mode only")
else:
    print("🚀 Running on Render - Supabase disabled for deployment stability")

def home(request):
    form = DataEntryForm()
    entries = DataEntry.objects.all().order_by('-date_created')
    
    # Metabase dashboard URL
    metabase_dashboard_url = get_metabase_dashboard_url()
    
    return render(request, 'home.html', {
        'form': form,
        'entries': entries,
        'metabase_url': metabase_dashboard_url,
        'supabase_connected': supabase is not None and 'RENDER' not in os.environ  # False on deployment
    })

@csrf_exempt
def add_entry(request):
    if request.method == 'POST':
        form = DataEntryForm(request.POST)
        if form.is_valid():
            # Save to Django database
            entry = form.save()
            
            # Also sync to Supabase if connected (and not on Render)
            if supabase and 'RENDER' not in os.environ:
                sync_to_supabase(entry)
            
            return redirect('home')
    
    return redirect('home')

def sync_to_supabase(entry):
    """Sync data to Supabase"""
    try:
        if supabase and 'RENDER' not in os.environ:  # Only sync locally
            data = {
                'name': entry.name,
                'email': entry.email,
                'age': entry.age,
                'salary': float(entry.salary),
                'department': entry.department,
                'django_id': entry.id,
                'date_created': entry.date_created.isoformat()
            }
            
            response = supabase.table('data_entries').insert(data).execute()
            print("✅ Data synced to Supabase")
            return response
    except Exception as e:
        print(f"❌ Error syncing to Supabase: {e}")

def get_metabase_dashboard_url():
    """Generate Metabase dashboard embed URL"""
    # For deployment, return empty string to show setup guide
    # This prevents errors since Metabase runs locally
    return ""