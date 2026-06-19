from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Message, Profile, TempUrl, Ticket, User


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]
    list_display = (
        'username', 'email', 'phone', 'is_admin', 'is_mentor',
        'is_mentee', 'is_verified', 'profile_completed', 'is_active',
    )
    list_filter = (
        'is_admin', 'is_mentor', 'is_mentee', 'is_verified',
        'profile_completed', 'is_staff', 'is_active',
    )
    search_fields = ('username', 'email', 'phone', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = (
        *BaseUserAdmin.fieldsets,
        ('Role & Status', {
            'fields': (
                'phone', 'is_admin', 'is_mentor', 'is_mentee',
                'accepted_terms', 'is_verified', 'profile_completed',
            ),
        }),
    )

    add_fieldsets = (
        *BaseUserAdmin.add_fieldsets,
        ('Role & Status', {
            'fields': (
                'email', 'phone', 'is_admin', 'is_mentor', 'is_mentee',
            ),
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'nationality', 'current_city', 'current_state', 'age')
    list_filter = ('gender', 'nationality', 'current_state')
    search_fields = ('user__username', 'user__email', 'nationality', 'current_city')
    raw_id_fields = ('user',)
    readonly_fields = ('age',)

    def age(self, obj):
        return obj.age
    age.short_description = 'Age'


@admin.register(TempUrl)
class TempUrlAdmin(admin.ModelAdmin):
    list_display = ('url_hash', 'user', 'date_created', 'expires')
    list_filter = ('expires',)
    search_fields = ('url_hash', 'user__username', 'user__email')
    raw_id_fields = ('user',)
    readonly_fields = ('date_created',)


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('sender', 'content', 'created_at', 'is_read')
    can_delete = False
    show_change_link = True


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    inlines = [MessageInline]
    list_display = ('ticket_id', 'subject', 'user', 'status', 'assigned_to', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('ticket_id', 'subject', 'user__username')
    readonly_fields = ('ticket_id', 'created_at', 'updated_at')
    raw_id_fields = ('user', 'assigned_to')
    list_editable = ('status',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'sender', 'content_preview', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('ticket__ticket_id', 'sender__username', 'content')
    raw_id_fields = ('ticket', 'sender', 'parent')
    readonly_fields = ('created_at',)
    list_editable = ('is_read',)

    def content_preview(self, obj):
        return obj.content[:80] + '...' if len(obj.content) > 80 else obj.content
    content_preview.short_description = 'Content'
