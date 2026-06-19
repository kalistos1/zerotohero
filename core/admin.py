from django.contrib import admin

from .models import (
    FAQ,
    AboutPage,
    Contact,
    ContactReply,
    Event,
    Gallery,
    GalleryCategory,
    SiteSettings,
    Testimonial,
    TeamMember,
    MentorshipApplication,
)

@admin.register(MentorshipApplication)
class MentorshipApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'mentorship_stream', 'experience_level', 'country', 'display_tech_interests', 'created_at')
    list_filter = ('mentorship_stream', 'experience_level', 'schedule_commitment', 'device_access', 'referral_source', 'created_at')
    search_fields = ('full_name', 'email', 'phone_number', 'country', 'python_community_name')
    readonly_fields = ('created_at',)

    def display_tech_interests(self, obj):
        return ', '.join(obj.get_tech_interests_list())
    display_tech_interests.short_description = 'Tech Interests'



@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'role')
    readonly_fields = ('created_at', 'updated_at')



@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('name', 'role', 'review_text')
    readonly_fields = ('created_at',)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('question', 'answer')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'read_status', 'has_reply', 'created_at')
    list_filter = ('read_status', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    list_editable = ('read_status',)
    readonly_fields = ('created_at',)

    def has_reply(self, obj):
        return obj.has_reply()
    has_reply.boolean = True
    has_reply.short_description = 'Replied'


@admin.register(ContactReply)
class ContactReplyAdmin(admin.ModelAdmin):
    list_display = ('contact', 'replied_by', 'created_at')
    readonly_fields = ('created_at', 'replied_by')



class GalleryInline(admin.TabularInline):
    model = Gallery
    extra = 1
    fields = ('title', 'media_type', 'image', 'media_url', 'position', 'is_active')


@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    inlines = [GalleryInline]
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'media_type', 'category', 'position', 'is_active', 'is_recent_display', 'created_at')
    list_filter = ('media_type', 'category', 'is_active', 'created_at')
    search_fields = ('title', 'caption', 'alt_text')
    list_editable = ('position', 'is_active')
    readonly_fields = ('created_at', 'updated_at')

    def is_recent_display(self, obj):
        return obj.is_recent()
    is_recent_display.boolean = True
    is_recent_display.short_description = 'Recent'


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'ceo_name', 'updated_at')
    readonly_fields = ('updated_at',)

    def has_add_permission(self, request):
        # Enforce singleton — only allow adding if none exists
        if AboutPage.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'status', 'venue', 'start_datetime',
        'end_datetime', 'is_free', 'entry_fee', 'is_active', 'created_at',
    )
    list_filter = ('status', 'is_active', 'is_free', 'start_datetime')
    search_fields = ('title', 'description', 'venue')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('status', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('created_by',)
    date_hierarchy = 'start_datetime'


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'support_email', 'support_phone')
    fieldsets = (
        ('General', {
            'fields': ('site_name', 'support_email', 'support_phone', 'whatsapp_number', 'address', 'working_hours'),
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url', 'youtube_url'),
        }),
    )

    def has_add_permission(self, request):
        # Enforce singleton — only allow adding if none exists
        if SiteSettings.objects.exists():
            return False
        return super().has_add_permission(request)
