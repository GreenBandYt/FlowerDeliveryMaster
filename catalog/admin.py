from django.contrib import admin
from .models import Product, Review

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'created_at', 'updated_at')  # Добавлено updated_at
    search_fields = ('name', 'description')  # Добавлено description
    list_filter = ('created_at', 'updated_at')  # Добавлено updated_at

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created_at')  # Для удобного просмотра
    list_filter = ('rating', 'created_at')  # Фильтры по рейтингу и дате
    search_fields = ('user__username', 'product__name', 'review_text')  # Поиск по тексту
