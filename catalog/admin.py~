from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'created_at', 'updated_at')  # Добавлено updated_at
    search_fields = ('name', 'description')  # Добавлено description
    list_filter = ('created_at', 'updated_at')  # Добавлено updated_at
