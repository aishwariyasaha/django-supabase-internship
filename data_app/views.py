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

# Check if we're on Render deployment
IS_RENDER = 'RENDER' in os.environ

# Initialize Supabase client ONLY if not on Render
supabase = None
supabase_connected = False

if not IS_RENDER:
    # Only attempt to import and use Supabase locally
    try:
        from supabase import create_client, Client
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if supabase_url and supabase_key:
            supabase = create_client(supabase_url, supabase_key)
            supabase_connected = True
            print("✅ Supabase client initialized successfully")
        else:
            print("⚠️ Supabase credentials not found")
    except ImportError:
        print("⚠️ Supabase package not available")
    except Exception as e:
        print(f"❌ Supabase initialization error: {e}")
else:
    print("🚀 Running on Render - Supabase disabled")

def home(request):
    form = DataEntryForm()
    entries = DataEntry.objects.all().order_by('-date_created')
    
    # Metabase dashboard URL
    metabase_dashboard_url = get_metabase_dashboard_url()
    
    return render(request, 'home.html', {
        'form': form,
        'entries': entries,
        'metabase_url': metabase_dashboard_url,
        'supabase_connected': supabase_connected and not IS_RENDER
    })

@csrf_exempt
def add_entry(request):
    if request.method == 'POST':
        form = DataEntryForm(request.POST)
        if form.is_valid():
            # Save to Django database
            entry = form.save()
            
            # Only sync to Supabase if running locally and connected
            if supabase_connected and not IS_RENDER and supabase:
                sync_to_supabase(entry)
            
            return redirect('home')
    
    return redirect('home')

def sync_to_supabase(entry):
    """Sync data to Supabase (local development only)"""
    if not IS_RENDER and supabase:
        try:
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
    # Return empty string to show setup guide on deployment
    return ""