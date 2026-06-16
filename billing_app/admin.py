from django.contrib import admin
from .models import Product , Bill , Billitem

admin.site.register(Product)
admin.site.register(Bill)
admin.site.register(Billitem)

# Register your models here.
