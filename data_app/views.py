from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import os
from .models import DataEntry
from .forms import DataEntryForm

def home(request):
    form = DataEntryForm()
    entries = DataEntry.objects.all().order_by('-date_created')
    
    # Check Supabase connection
    supabase_connected = check_supabase_connection()
    
    return render(request, 'home.html', {
        'form': form,
        'entries': entries,
        'metabase_url': "",
        'supabase_connected': supabase_connected
    })

@csrf_exempt
def add_entry(request):
    if request.method == 'POST':
        form = DataEntryForm(request.POST)
        if form.is_valid():
            entry = form.save()
            
            # Try to sync with Supabase
            sync_to_supabase(entry)
            
            return redirect('home')
    return redirect('home')

def check_supabase_connection():
    """Check if Supabase connection works"""
    try:
        from supabase import create_client
        import os
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if supabase_url and supabase_key:
            # Test connection
            supabase = create_client(supabase_url, supabase_key)
            # Simple query to test connection
            result = supabase.table('data_entries').select('*').limit(1).execute()
            return True
    except:
        pass
    return False

def sync_to_supabase(entry):
    """Sync data to Supabase with error handling"""
    try:
        from supabase import create_client
        import os
        
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
            return True
    except Exception as e:
        print(f"Supabase sync failed: {e}")
    return False