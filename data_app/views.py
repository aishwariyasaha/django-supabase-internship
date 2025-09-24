from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.db.models import Avg, Max, Min, Sum, Count
from .models import DataEntry
from .forms import DataEntryForm

def home(request):
    try:
        form = DataEntryForm()
        entries = DataEntry.objects.all().order_by('-date_created')
        
        # Calculate real statistics
        total_employees = entries.count()
        
        # Department statistics
        department_stats = entries.values('department').annotate(count=Count('id')).order_by('-count')
        
        department_counts = []
        unique_departments = set()
        
        for dept in department_stats:
            percentage = (dept['count'] / total_employees * 100) if total_employees > 0 else 0
            department_counts.append({
                'name': dept['department'],
                'count': dept['count'],
                'percentage': round(percentage, 1)
            })
            unique_departments.add(dept['department'])
        
        # Salary statistics
        if entries:
            salary_stats = entries.aggregate(
                avg_salary=Avg('salary'),
                total_salary=Sum('salary'),
                max_salary=Max('salary'),
                min_salary=Min('salary')
            )
            average_salary = salary_stats['avg_salary'] or 0
            total_salary = salary_stats['total_salary'] or 0
            max_salary = salary_stats['max_salary'] or 0
            min_salary = salary_stats['min_salary'] or 0
            
            # Age statistics
            age_stats = entries.aggregate(avg_age=Avg('age'))
            avg_age = age_stats['avg_age'] or 0
        else:
            average_salary = 0
            total_salary = 0
            max_salary = 0
            min_salary = 0
            avg_age = 0
        
        # Test database connection
        supabase_connected = False
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            supabase_connected = True
        except:
            supabase_connected = False
        
        return render(request, 'home.html', {
            'form': form,
            'entries': entries,
            'total_employees': total_employees,
            'department_counts': department_counts,
            'unique_departments': list(unique_departments),
            'average_salary': average_salary,
            'total_salary': total_salary,
            'max_salary': max_salary,
            'min_salary': min_salary,
            'avg_age': avg_age,
            'supabase_connected': supabase_connected
        })
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")

@csrf_exempt
def add_entry(request):
    if request.method == 'POST':
        try:
            form = DataEntryForm(request.POST)
            if form.is_valid():
                entry = form.save()
                print(f"✅ Entry saved to database! ID: {entry.id}")
                return redirect('home')
            else:
                print("❌ Form errors:", form.errors)
        except Exception as e:
            print(f"❌ Database error: {e}")
    return redirect('home')

def test_supabase(request):
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()
        
        # Test creating a record
        test_entry = DataEntry.objects.create(
            name="Supabase Test User",
            email="test@supabase.com",
            age=25,
            salary=45000,
            department="Testing"
        )
        
        # Count total entries
        total_entries = DataEntry.objects.count()
        
        return JsonResponse({
            'status': 'success',
            'database_version': db_version[0],
            'test_entry_id': test_entry.id,
            'total_entries': total_entries,
            'message': 'Supabase connection successful!'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

def list_entries_api(request):
    try:
        entries = DataEntry.objects.all().order_by('-date_created')
        entries_list = []
        for entry in entries:
            entries_list.append({
                'id': entry.id,
                'name': entry.name,
                'email': entry.email,
                'age': entry.age,
                'salary': float(entry.salary),
                'department': entry.department,
                'date_created': entry.date_created.isoformat()
            })
        
        return JsonResponse({
            'status': 'success',
            'total_entries': len(entries_list),
            'entries': entries_list
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })