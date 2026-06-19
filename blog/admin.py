from django.contrib import admin
from .models import Post, BlogCategory

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'date_created', 'category')
    list_filter = ('status', 'date_created', 'category')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
