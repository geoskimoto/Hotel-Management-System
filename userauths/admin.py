from django.contrib import admin
from userauths.models import User, Profile, MemberApplication, ApprovedEmail

class UserAdmin(admin.ModelAdmin):
    search_fields  = ['full_name', 'username', 'email',  'phone', 'gender']
    list_display  = ['full_name', 'username', 'email',  'phone', 'gender']

class ProfileAdmin(admin.ModelAdmin):
    search_fields  = ['user__username', 'full_name']
    list_display = ['thumbnail', 'user', 'full_name', 'verified']

class ApprovedEmailAdmin(admin.ModelAdmin):
    list_display = ('email',)
    
    
admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(MemberApplication)
admin.site.register(ApprovedEmail, ApprovedEmailAdmin)