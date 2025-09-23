from django.db import models

class DataEntry(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    age = models.IntegerField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    department = models.CharField(max_length=50)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'data_entries'
    
    def __str__(self):
        return f"{self.name} - {self.department}"